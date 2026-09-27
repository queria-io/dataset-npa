"""警察庁「特殊詐欺の認知・検挙状況等について」の手口別・月別の表の取得・整形。

警察庁が公表する統計データ（Excel）から、特殊詐欺全体と手口別の月別表
（認知件数・うち既遂・実質的な被害総額・検挙件数・検挙人員）を取り出し、
手口×年月の CSV へ正規化する。形態（文言）別の内訳表と、組織的犯罪処罰法違反などの
関連法令の表は扱わない。

手口の区分は2度変わっている。令和2年に預貯金詐欺がオレオレ詐欺から分かれて10類型になり、
令和8年にニセ警察詐欺が独立し、SNS型投資詐欺・SNS型ロマンス詐欺が特殊詐欺の手口に加わった。
各ファイルは当年と前年の表を持ち、前年の表も当年と同じ区分で集計されている。
区分が変わった年のファイルは前年を新しい区分で組み替えて載せるので、2025年は2つの区分で重なる。
どちらの区分かを classification_year（区分の適用開始年）で持ち、行を混ぜない。

同じ区分×年の表が複数のファイルにあるときは、年別ファイルの当年の表、最新ファイルの表、
年別ファイルの前年の表の順に採る。年別ファイルを足しても重ならず、区分が変わった年の組み替え分は
最新ファイルが次の年に進んでも翌年の年別ファイルから採り続けられる。
"""

import csv
import io
import re
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

import openpyxl

BASE_URL = "https://www.npa.go.jp/bureau/criminal/souni/tokusyusagi/"

# 年別の確定値ファイル。2024 年分は訂正版が出ているので訂正版を使う。
# 新しい年の確定値が公表されたらここに足す（上半期の暫定値のファイルは足さない）。
# https://www.npa.go.jp/publications/statistics/sousa/sagi.html
YEARLY_FILES = {
    2020: "tokushusagi_toukei2020.xlsx",
    2021: "tokushusagi_toukei2021.xlsx",
    2022: "tokushusagi_toukei2022.xlsx",
    2023: "hurikomesagi_toukei2023.xlsx",
    2024: "hurikomesagi_toukei2024_teisei.xlsx",
    2025: "hurikomesagi_toukei2025.xlsx",
}

# 最新の暫定値のファイル。当年（暫定・公表月まで）と前年の2年を持つ。
LATEST_FILE = "hurikomesagi_toukei.xlsx"

FETCH_ATTEMPTS = 3
FETCH_BACKOFF_SEC = 5.0

# 手口の表の見出し（例: 「２－４(1)　オレオレ詐欺」「１　特殊詐欺」）。
# 見出しは NFKC 正規化後に照合する。「(2)」は形態（文言）別の内訳表、
# 3 以降は組織的犯罪処罰法違反などの関連法令の表なので採らない。
SECTION = re.compile(r"^(\d+(?:-\d+)?)(?:\((\d)\))?\s+(.+)$")

ERA = re.compile(r"^(令和|平成)(元|\d+)年$")

# 行ラベル（先頭一致） -> 列。被害額は手口によって載る行が違う。
# 実質的な被害総額は ATM から引き出された額を加えた額で、還付金詐欺の表には無い。
# 被害総額（既遂のみ）は還付金詐欺と一部の手口にだけある。どちらも公表どおりに持ち、無い方は NULL。
METRICS = {
    "認知件数": "recognized_cases",
    "うち既遂": "completed_cases",
    "実質的な被害総額": "damage_amount_yen",
    "被害総額(既遂のみ)": "completed_damage_amount_yen",
    "検挙件数": "cleared_cases",
    "検挙人員": "arrested_persons",
}
REQUIRED_METRICS = {"recognized_cases", "completed_cases", "cleared_cases", "arrested_persons"}
DAMAGE_METRICS = {"damage_amount_yen", "completed_damage_amount_yen"}

OUTPUT_COLUMNS = [
    "classification_year", "year", "month", "modus", "is_provisional",
    *METRICS.values(),
]


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(1, FETCH_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == FETCH_ATTEMPTS:
                raise
            print(f"  retry {attempt}/{FETCH_ATTEMPTS - 1}: {url} ({exc})")
            time.sleep(FETCH_BACKOFF_SEC * attempt)
    raise AssertionError("unreachable")


def _text(value) -> str:
    return unicodedata.normalize("NFKC", str(value)).strip()


def _era_year(value) -> int | None:
    m = ERA.match(_text(value))
    if not m:
        return None
    n = 1 if m[2] == "元" else int(m[2])
    return (2018 if m[1] == "令和" else 1988) + n


def _number(value) -> int | None:
    # 「-」は統計を取っていない（ニセ警察詐欺の令和7年の検挙など）
    if value is None or value == "" or _text(value) == "-":
        return None
    number = float(value)
    if number != int(number):
        raise ValueError(f"non-integer value: {value}")
    return int(number)


def _metric(label: str) -> str | None:
    for prefix, column in METRICS.items():
        if label.replace(" ", "").startswith(prefix):
            return column
    return None


def _parse_blocks(content: bytes) -> list[dict]:
    """シートを上から走査し、手口ごとの年別ブロック（1年×12か月）を返す。

    ブロックは「令和N年」の行、「合計(１月～N月)／１月…１２月」の見出し行、
    指標の行の順に並び、空行で終わる。
    """
    sheet = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True).worksheets[0]
    blocks, modus, block = [], None, None
    for row in sheet.iter_rows(values_only=True):
        cells = [(j, c) for j, c in enumerate(row) if c not in (None, "")]
        if not cells:
            block = None
            continue
        j0, c0 = cells[0]
        label = _text(c0)

        section = SECTION.match(label) if j0 <= 1 else None
        if section:
            is_modus = section[1] == "1" or section[1].startswith("2-")
            modus = section[3] if is_modus and section[2] != "2" else None
            block = None
            continue
        if modus is None:
            continue
        if len(cells) == 1 and _era_year(c0):
            block = {"modus": modus, "year": _era_year(c0), "months": None, "rows": {}}
            blocks.append(block)
            continue
        if block is None:
            continue
        if label.startswith("合計"):
            m = re.search(r"~(\d+)月", label)  # NFKC で「～」は「~」になる
            block["through"] = int(m[1]) if m else 12
            block["months"] = {j: int(_text(c).removesuffix("月")) for j, c in cells[1:]}
            block["total_col"] = j0
            continue
        column = _metric(label) if j0 <= 3 else None
        if column and block["months"]:
            block["rows"][column] = {
                "total": _number(row[block["total_col"]]),
                "by_month": {mo: _number(row[j]) for j, mo in block["months"].items()},
            }
    return [b for b in blocks if b["rows"]]


def _to_rows(block: dict, classification_year: int, provisional: bool) -> list[list]:
    missing = REQUIRED_METRICS - set(block["rows"])
    if missing or not DAMAGE_METRICS & set(block["rows"]):
        raise ValueError(f"{block['year']} {block['modus']}: 指標が欠けている: {sorted(block['rows'])}")

    # 合計列は「１月～N月」の合計。月の値を足して一致することを確かめる
    for column, values in block["rows"].items():
        if values["total"] is None:
            continue
        summed = sum(values["by_month"][mo] or 0 for mo in range(1, block["through"] + 1))
        if summed != values["total"]:
            raise ValueError(
                f"{block['year']} {block['modus']} {column}: 月の合計 {summed} が合計列 {values['total']} と違う"
            )

    # 暫定の年は公表月より後の月が 0 で埋まっているので落とす
    last_month = block["through"] if provisional else 12
    return [
        [
            classification_year, block["year"], month, block["modus"], provisional,
            *(block["rows"].get(c, {"by_month": {}})["by_month"].get(month) for c in METRICS.values()),
        ]
        for month in range(1, last_month + 1)
    ]


def _classification_year(blocks: list[dict]) -> int:
    return 2026 if any(b["modus"] == "ニセ警察詐欺" for b in blocks) else 2020


def download_and_normalize(csv_path: Path) -> int:
    # (区分, 年) -> (優先順位, ファイル名, 行)。優先順位の小さい方を採る
    tables: dict[tuple[int, int], tuple[int, str, list[list]]] = {}

    def offer(rank: int, name: str, classification: int, year: int, blocks: list[dict], provisional: bool):
        rows = [r for b in blocks for r in _to_rows(b, classification, provisional)]
        key = (classification, year)
        if key not in tables or rank < tables[key][0]:
            tables[key] = (rank, name, rows)

    first_year = min(YEARLY_FILES)
    for year, name in YEARLY_FILES.items():
        blocks = _parse_blocks(_fetch(BASE_URL + name))
        classification = _classification_year(blocks)
        own = [b for b in blocks if b["year"] == year]
        if not own:
            raise ValueError(f"{name}: {year} 年の表が見つからない")
        offer(0, name, classification, year, own, provisional=False)
        # 収録開始より前の年は区分が違っても組み替えられていないので採らない
        prior = [b for b in blocks if b["year"] == year - 1]
        if prior and year - 1 >= first_year:
            offer(2, name, classification, year - 1, prior, provisional=False)

    blocks = _parse_blocks(_fetch(BASE_URL + LATEST_FILE))
    classification = _classification_year(blocks)
    current = max(b["year"] for b in blocks)
    for year in sorted({b["year"] for b in blocks}):
        offer(1, LATEST_FILE, classification, year,
              [b for b in blocks if b["year"] == year], provisional=year == current)

    rows = []
    for (classification, year), (_, name, table_rows) in sorted(tables.items()):
        print(f"  {classification} {year}: {name}, {len(table_rows)} rows")
        rows.extend(table_rows)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_COLUMNS)
        writer.writerows(rows)
    return len(rows)
