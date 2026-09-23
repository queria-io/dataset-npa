"""警察庁 犯罪統計資料（確定値）の都道府県別表の取得・整形。

警察庁が年1回公表する「犯罪統計資料（1～12月分【確定値】）」の Excel（e-Stat 掲載）から、
都道府県別の表（第3表・第4表・第6表・第9表）を取り出し、罪種×地域の縦持ち CSV へ正規化する。
各表は当年と前年を並べた対前年比較の形なので、当年の列だけを採る。
月次の暫定値は確定値で数字が変わるため扱わない。

シートの配置は 2020 年分から同じで、2019 年分以前は列構成が違うため対象外にしている。
"""

import csv
import time
import urllib.error
import urllib.request
from pathlib import Path

import xlrd

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

DOWNLOAD_URL = "https://www.e-stat.go.jp/stat-search/file-download?statInfId={}&fileKind=0"

FETCH_ATTEMPTS = 3
FETCH_BACKOFF_SEC = 5.0

# シート名 -> 罪種名。2023 年の刑法改正で強制性交等・強制わいせつは
# 不同意性交等・不同意わいせつに名前と構成要件が変わったので、公表どおりの名前で持つ。
SHEETS = {
    "第３表": "刑法犯総数",
    "第４表": "窃盗犯総数",
    "第６表＿重要犯罪": "重要犯罪総数",
    "殺人": "殺人",
    "強盗": "強盗",
    "侵入強盗": "侵入強盗",
    "放火": "放火",
    "強制性交等": "強制性交等",
    "不同意性交等": "不同意性交等",
    "略取誘拐・人身売買": "略取誘拐・人身売買",
    "強制わいせつ": "強制わいせつ",
    "不同意わいせつ": "不同意わいせつ",
    "重要窃盗犯": "重要窃盗犯総数",
    "侵入盗": "侵入盗",
    "住宅対象": "侵入盗（住宅対象）",
    "その他": "侵入盗（その他）",
    "自動車盗": "自動車盗",
    "ひったくり": "ひったくり",
    "すり": "すり",
    "第９表＿主な街頭犯罪総数": "主な街頭犯罪総数",
    "器物損壊": "器物損壊",
    "住居侵入": "住居侵入",
}

# 1 年分のファイルに揃うはずの罪種数（強制/不同意の2組はどちらか一方だけ存在する）
SHEETS_PER_YEAR = len(SHEETS) - 2

# データ行の位置と列（2020 年分以降の共通レイアウト）
FIRST_ROW = 5          # 総数の行
LAST_ROW = 64          # 沖縄県の行
COL_GROUP, COL_AREA = 0, 1
COL_RECOGNIZED, COL_CLEARED, COL_ARRESTED = 2, 6, 10

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


def _count(value) -> int:
    # 件数はすべて整数だが xlrd は数値セルを float で返す
    if value == "" or value is None:
        raise ValueError("empty count cell")
    number = float(value)
    if number != int(number):
        raise ValueError(f"non-integer count: {value}")
    return int(number)


def _parse_sheet(sheet: xlrd.sheet.Sheet, year: int, crime_type: str) -> list[list]:
    header = str(sheet.cell_value(4, COL_RECOGNIZED))
    if not header.startswith(f"{year}年"):
        raise ValueError(f"{year} {sheet.name}: 当年列の見出しが想定と違う: {header!r}")
    last = str(sheet.cell_value(LAST_ROW, COL_AREA)).strip()
    if last != "沖縄県":
        raise ValueError(f"{year} {sheet.name}: 最終行が沖縄県でない: {last!r}")

    rows = []
    for r in range(FIRST_ROW, LAST_ROW + 1):
        group = str(sheet.cell_value(r, COL_GROUP)).strip()
        area = str(sheet.cell_value(r, COL_AREA)).strip()
        if r == FIRST_ROW:
            # 全国の行。第9表は「主な街頭犯罪総数」と罪種名で書かれている
            group, area = "全国", "総数"
        rows.append([
            year, crime_type, group, area,
            _count(sheet.cell_value(r, COL_RECOGNIZED)),
            _count(sheet.cell_value(r, COL_CLEARED)),
            _count(sheet.cell_value(r, COL_ARRESTED)),
        ])
    return rows


def _parse_year(content: bytes, year: int) -> list[list]:
    book = xlrd.open_workbook(file_contents=content)
    names = set(book.sheet_names())
    found = [name for name in SHEETS if name in names]
    if len(found) != SHEETS_PER_YEAR:
        missing = sorted(set(SHEETS) - names)
        raise ValueError(f"{year}: 都道府県別のシートが揃っていない（欠け: {missing}）")

    rows = []
    for name in found:
        rows.extend(_parse_sheet(book.sheet_by_name(name), year, SHEETS[name]))
    return rows


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
