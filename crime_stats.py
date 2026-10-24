"""警察庁 犯罪統計資料（確定値）の都道府県別表の取得・整形。

警察庁が年1回公表する「犯罪統計資料（1～12月分【確定値】）」の CSV（e-Stat 掲載）から、
都道府県別の表（第3表・第4表・第6表・第9表）を取り出し、罪種×地域の縦持ち CSV へ正規化する。
各表は当年と前年を並べた対前年比較の形なので、当年の列だけを採る。
月次の暫定値は確定値で数字が変わるため扱わない。

CSV は全表を1ファイルに縦に積んだもので、「第N表」の行で表を切り分ける。
表の中の配置は 2020 年分から同じで、2019 年分以前は列構成が違うため対象外にしている。
"""

import csv
import io
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

# 対象年 -> e-Stat のファイル ID（statInfId）。警察庁「犯罪統計」の各年の確定値ページから引く。
# https://www.npa.go.jp/publications/statistics/sousa/statistics.html
STAT_INF_IDS = {
    2020: "000032049031",
    2021: "000032168154",
    2022: "000040015380",
    2023: "000040141107",
    2024: "000040247461",
    2025: "000040410682",
}

# e-Stat は Excel（fileKind=0）を取り下げ、全表を縦に積んだ CSV（fileKind=1、Shift_JIS）だけを配る
DOWNLOAD_URL = "https://www.e-stat.go.jp/stat-search/file-download?statInfId={}&fileKind=1"
ENCODING = "cp932"

FETCH_ATTEMPTS = 3
FETCH_BACKOFF_SEC = 5.0

# 表の見出しの括弧書き -> 罪種名。2023 年の刑法改正で強制性交等・強制わいせつは
# 不同意性交等・不同意わいせつに名前と構成要件が変わったので、公表どおりの名前で持つ。
# 侵入盗の内訳は年で書き方が違う（2020 年は「住宅対象侵入盗」、2021 年以降は「侵入盗－住宅対象」）。
TABLE6_TYPES = {
    "重要犯罪総数": "重要犯罪総数",
    "殺人": "殺人",
    "強盗": "強盗",
    "侵入強盗": "侵入強盗",
    "放火": "放火",
    "強制性交等": "強制性交等",
    "不同意性交等": "不同意性交等",
    "略取誘拐・人身売買": "略取誘拐・人身売買",
    "強制わいせつ": "強制わいせつ",
    "不同意わいせつ": "不同意わいせつ",
    "重要窃盗犯総数": "重要窃盗犯総数",
    "侵入盗": "侵入盗",
    "住宅対象侵入盗": "侵入盗（住宅対象）",
    "侵入盗－住宅対象": "侵入盗（住宅対象）",
    "侵入盗その他": "侵入盗（その他）",
    "侵入盗－その他": "侵入盗（その他）",
    "自動車盗": "自動車盗",
    "ひったくり": "ひったくり",
    "すり": "すり",
}

# 第9表は3つの表が同じ見出しで並ぶ。どれかは小見出しの罪種名で見分ける
TABLE9_TYPES = ("主な街頭犯罪総数", "器物損壊", "住居侵入")

# 1 年分のファイルに揃うはずの罪種数
# （第3表・第4表・第6表の重要犯罪総数と14罪種・第9表の3つ。強制/不同意はどちらか一方）
TYPES_PER_YEAR = 3 + 14 + 3

# 表の先頭からの行の位置と列（2020 年分以降の共通レイアウト）
HEADER_ROW = 4         # 当年・前年の見出しの行
FIRST_ROW = 5          # 総数の行
LAST_ROW = 64          # 沖縄県の行
COL_GROUP, COL_AREA = 0, 1
COL_RECOGNIZED, COL_CLEARED, COL_ARRESTED = 2, 6, 10

TABLE_NUMBER = re.compile(r"^第([０-９]+)表$")
PAREN = re.compile(r"（([^（）]+)）\s*$")

OUTPUT_COLUMNS = [
    "year", "crime_type", "area_group", "area",
    "recognized_cases", "cleared_cases", "arrested_persons",
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


def _cell(rows: list[list[str]], r: int, c: int) -> str:
    row = rows[r] if r < len(rows) else []
    return row[c].strip() if c < len(row) else ""


def _count(value: str) -> int:
    # CSV の件数は数字の後ろに空白が付く
    if value == "":
        raise ValueError("empty count cell")
    return int(value)


def _table_starts(rows: list[list[str]]) -> list[tuple[int, str, str]]:
    """表の先頭行ごとに (行番号, 表番号, 見出し)。見出しは表番号の後ろのセルのどれかにある"""
    return [
        (r, m.group(1), "".join(cell.strip() for cell in row[1:]))
        for r, row in enumerate(rows)
        if row and (m := TABLE_NUMBER.match(row[0].strip()))
    ]


def _crime_type(rows: list[list[str]], start: int, number: str, title: str) -> str | None:
    if number == "３":
        return "刑法犯総数"
    if number == "４":
        return "窃盗犯総数"
    if number == "６":
        paren = PAREN.search(title)
        if paren is None or paren.group(1) not in TABLE6_TYPES:
            raise ValueError(f"第6表の罪種が想定外: {title!r}")
        return TABLE6_TYPES[paren.group(1)]
    if number == "９":
        # 小見出し（「（２） 器物損壊　都道府県別…」）か総数の行に罪種名がある
        text = "".join(cell for row in rows[start + 1:start + FIRST_ROW + 1] for cell in row)
        found = [name for name in TABLE9_TYPES if name in text]
        if len(found) != 1:
            raise ValueError(f"第9表の罪種を見分けられない（行 {start}）: {rows[start + 1][:1]}")
        return found[0]
    return None


def _parse_table(rows: list[list[str]], start: int, year: int, crime_type: str) -> list[list]:
    header = _cell(rows, start + HEADER_ROW, COL_RECOGNIZED)
    if not header.startswith(f"{year}年"):
        raise ValueError(f"{year} {crime_type}: 当年列の見出しが想定と違う: {header!r}")
    last = _cell(rows, start + LAST_ROW, COL_AREA)
    if last != "沖縄県":
        raise ValueError(f"{year} {crime_type}: 最終行が沖縄県でない: {last!r}")

    def row_of(r: int) -> list:
        # 全国の行。第9表は「主な街頭犯罪総数」と罪種名で書かれている
        group, area = ("全国", "総数") if r == start + FIRST_ROW else (
            _cell(rows, r, COL_GROUP), _cell(rows, r, COL_AREA)
        )
        return [
            year, crime_type, group, area,
            _count(_cell(rows, r, COL_RECOGNIZED)),
            _count(_cell(rows, r, COL_CLEARED)),
            _count(_cell(rows, r, COL_ARRESTED)),
        ]

    return [row_of(r) for r in range(start + FIRST_ROW, start + LAST_ROW + 1)]


def _parse_year(content: bytes, year: int) -> list[list]:
    rows = list(csv.reader(io.StringIO(content.decode(ENCODING))))
    tables = [
        (start, crime_type)
        for start, number, title in _table_starts(rows)
        if (crime_type := _crime_type(rows, start, number, title)) is not None
    ]
    types = [crime_type for _, crime_type in tables]
    if len(types) != TYPES_PER_YEAR or len(set(types)) != len(types):
        raise ValueError(f"{year}: 都道府県別の表が揃っていない（見つかった表: {types}）")
    return [row for start, crime_type in tables for row in _parse_table(rows, start, year, crime_type)]


def download_and_normalize(csv_path: Path) -> int:
    rows = []
    for year, stat_inf_id in STAT_INF_IDS.items():
        content = _fetch(DOWNLOAD_URL.format(stat_inf_id))
        year_rows = _parse_year(content, year)
        print(f"  {year}: {len(year_rows)} rows")
        rows.extend(year_rows)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_COLUMNS)
        writer.writerows(rows)
    return len(rows)
