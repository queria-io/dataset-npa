"""警視庁 区市町村の町丁別、罪種別及び手口別認知件数（年累計）の取得・整形。

警視庁が年1回公表する町丁字単位の認知件数表を、1年×1町丁字で1行の CSV へ正規化する。
2009〜2016 年分は区市町村ごとのシートに分かれた Excel、2017 年分以降は全区市町村を
1表にした CSV（CP932）で配られる。列（罪種・手口の37区分）はどの年も同じ並び。

当年の月累計（年途中の値）は扱わない。区市町村計と合計の行は町丁字の行の合計と
一致することを確かめてから捨て、23区計・多摩地区・島部計の行は読み飛ばす。他県・海外認知・
不明の行は町丁字に属さないので収録しない。町丁字名は全角空白を除いて両方の期で揃える
（原表は「鶴間　（旧）」のように町名と（旧）の間に全角空白を入れる年と入れない年がある）。
"""

import csv
import io
import time
import urllib.error
import urllib.request
from pathlib import Path

import openpyxl
import xlrd

BASE_URL = "https://www.keishicho.metro.tokyo.lg.jp/about_mpd/jokyo_tokei/jokyo/ninchikensu.files/"

# 対象年 -> 配布ファイル名。年が明けて年累計が出たらここに足す。
FILES = {
    2009: "H21.xls",
    2010: "H22.xls",
    2011: "H23.xls",
    2012: "H24.xls",
    2013: "H25.xls",
    2014: "H26.xls",
    2015: "H27.xls",
    2016: "H28.xlsx",
    2017: "H29.csv",
    2018: "H30.csv",
    2019: "H31.csv",
    2020: "R2.csv",
    2021: "R3.csv",
    2022: "R4.csv",
    2023: "R5.csv",
    2024: "R6.csv",
    2025: "R7.csv",
}

FETCH_ATTEMPTS = 3
FETCH_BACKOFF_SEC = 5.0

# 原表での区市町村名 -> (全国地方公共団体コード, 名称)。
# 原表は郡名・島名を前に付けて書く町村がある（西多摩郡瑞穂町・三宅島三宅村など）。
MUNICIPALITIES = {
    "千代田区": ("131016", "千代田区"),
    "中央区": ("131024", "中央区"),
    "港区": ("131032", "港区"),
    "新宿区": ("131041", "新宿区"),
    "文京区": ("131059", "文京区"),
    "台東区": ("131067", "台東区"),
    "墨田区": ("131075", "墨田区"),
    "江東区": ("131083", "江東区"),
    "品川区": ("131091", "品川区"),
    "目黒区": ("131105", "目黒区"),
    "大田区": ("131113", "大田区"),
    "世田谷区": ("131121", "世田谷区"),
    "渋谷区": ("131130", "渋谷区"),
    "中野区": ("131148", "中野区"),
    "杉並区": ("131156", "杉並区"),
    "豊島区": ("131164", "豊島区"),
    "北区": ("131172", "北区"),
    "荒川区": ("131181", "荒川区"),
    "板橋区": ("131199", "板橋区"),
    "練馬区": ("131202", "練馬区"),
    "足立区": ("131211", "足立区"),
    "葛飾区": ("131229", "葛飾区"),
    "江戸川区": ("131237", "江戸川区"),
    "八王子市": ("132012", "八王子市"),
    "立川市": ("132021", "立川市"),
    "武蔵野市": ("132039", "武蔵野市"),
    "三鷹市": ("132047", "三鷹市"),
    "青梅市": ("132055", "青梅市"),
    "府中市": ("132063", "府中市"),
    "昭島市": ("132071", "昭島市"),
    "調布市": ("132080", "調布市"),
    "町田市": ("132098", "町田市"),
    "小金井市": ("132101", "小金井市"),
    "小平市": ("132110", "小平市"),
    "日野市": ("132128", "日野市"),
    "東村山市": ("132136", "東村山市"),
    "国分寺市": ("132144", "国分寺市"),
    "国立市": ("132152", "国立市"),
    "福生市": ("132187", "福生市"),
    "狛江市": ("132195", "狛江市"),
    "東大和市": ("132209", "東大和市"),
    "清瀬市": ("132217", "清瀬市"),
    "東久留米市": ("132225", "東久留米市"),
    "武蔵村山市": ("132233", "武蔵村山市"),
    "多摩市": ("132241", "多摩市"),
    "稲城市": ("132250", "稲城市"),
    "羽村市": ("132276", "羽村市"),
    "あきる野市": ("132284", "あきる野市"),
    "西東京市": ("132292", "西東京市"),
    "西多摩郡瑞穂町": ("133035", "瑞穂町"),
    "西多摩郡日の出町": ("133051", "日の出町"),
    "西多摩郡檜原村": ("133078", "檜原村"),
    "西多摩郡奥多摩町": ("133086", "奥多摩町"),
    "大島町": ("133612", "大島町"),
    "利島村": ("133621", "利島村"),
    "新島村": ("133639", "新島村"),
    "神津島村": ("133647", "神津島村"),
    "三宅島三宅村": ("133817", "三宅村"),
    "御蔵島村": ("133825", "御蔵島村"),
    "八丈島八丈町": ("134015", "八丈町"),
    "青ヶ島村": ("134023", "青ヶ島村"),
    "小笠原村": ("134210", "小笠原村"),
}

# 区市町村名の前方一致で町丁字を切り出すので、長い名前から当てる（「北区」と「…北区」の取り違え防止）
MUNICIPALITY_PREFIXES = sorted(MUNICIPALITIES, key=len, reverse=True)

# 原表の37列（総合計＋罪種・手口）。CSV の見出しと同じ並び。
COUNT_COLUMNS = [
    ("総合計", "total"),
    ("凶悪犯計", "heinous_total"),
    ("凶悪犯強盗", "heinous_robbery"),
    ("凶悪犯その他", "heinous_other"),
    ("粗暴犯計", "violent_total"),
    ("粗暴犯凶器準備集合", "violent_unlawful_assembly"),
    ("粗暴犯暴行", "violent_assault"),
    ("粗暴犯傷害", "violent_injury"),
    ("粗暴犯脅迫", "violent_intimidation"),
    ("粗暴犯恐喝", "violent_extortion"),
    ("侵入窃盗計", "burglary_total"),
    ("侵入窃盗金庫破り", "burglary_safe"),
    ("侵入窃盗学校荒し", "burglary_school"),
    ("侵入窃盗事務所荒し", "burglary_office"),
    ("侵入窃盗出店荒し", "burglary_shop"),
    ("侵入窃盗空き巣", "burglary_vacant_house"),
    ("侵入窃盗忍込み", "burglary_night"),
    ("侵入窃盗居空き", "burglary_occupied_house"),
    ("侵入窃盗その他", "burglary_other"),
    ("非侵入窃盗計", "non_burglary_total"),
    ("非侵入窃盗自動車盗", "non_burglary_car"),
    ("非侵入窃盗オートバイ盗", "non_burglary_motorcycle"),
    ("非侵入窃盗自転車盗", "non_burglary_bicycle"),
    ("非侵入窃盗車上ねらい", "non_burglary_from_car"),
    ("非侵入窃盗自販機ねらい", "non_burglary_vending_machine"),
    ("非侵入窃盗工事場ねらい", "non_burglary_construction_site"),
    ("非侵入窃盗すり", "non_burglary_pickpocket"),
    ("非侵入窃盗ひったくり", "non_burglary_snatching"),
    ("非侵入窃盗置引き", "non_burglary_unattended"),
    ("非侵入窃盗万引き", "non_burglary_shoplifting"),
    ("非侵入窃盗その他", "non_burglary_other"),
    ("その他計", "other_total"),
    ("その他詐欺", "other_fraud"),
    ("その他占有離脱物横領", "other_embezzlement_lost_property"),
    ("その他その他知能犯", "other_intellectual"),
    ("その他賭博", "other_gambling"),
    ("その他その他刑法犯", "other_penal_code"),
]
N_COUNTS = len(COUNT_COLUMNS)

# 計の内訳。罪種の計 = 手口の合計、総合計 = 罪種の計の合計。
SUBTOTALS = {1: (2, 4), 4: (5, 10), 10: (11, 19), 19: (20, 31), 31: (32, 37)}
CATEGORY_TOTALS = tuple(SUBTOTALS)

# 町丁字に属さない行（収録しない）
NON_TOWN_ROWS = {"他県", "海外認知", "不明"}

# Excel 期のシート内レイアウト
EXCEL_FIRST_DATA_ROW = 7
EXCEL_SUMMARY_SHEET = "最終"

OUTPUT_COLUMNS = ["year", "city_code", "municipality", "town"] + [c for _, c in COUNT_COLUMNS]


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
    # xlrd は数値セルを float で返し、openpyxl は int で返す。空セルは無い前提
    if value == "" or value is None:
        raise ValueError("empty count cell")
    number = float(value)
    if number != int(number):
        raise ValueError(f"non-integer count: {value}")
    return int(number)


def _check_subtotals(label: str, counts: list[int]) -> None:
    for total, (start, end) in SUBTOTALS.items():
        if counts[total] != sum(counts[start:end]):
            raise ValueError(f"{label}: {COUNT_COLUMNS[total][0]} が内訳の合計と合わない")
    if counts[0] != sum(counts[i] for i in CATEGORY_TOTALS):
        raise ValueError(f"{label}: 総合計が罪種の計の合計と合わない")


def _sum(rows: list[list[int]]) -> list[int]:
    return [sum(col) for col in zip(*rows)] if rows else [0] * N_COUNTS


class _Year:
    """1年分の行を集め、計の行と突き合わせる。"""

    def __init__(self, year: int):
        self.year = year
        self.towns: dict[str, list[tuple[str, list[int]]]] = {name: [] for name in MUNICIPALITIES}
        self.municipality_totals: dict[str, list[int]] = {}
        self.other_rows: dict[str, list[int]] = {}

    def add_town(self, municipality: str, town: str, counts: list[int]) -> None:
        _check_subtotals(f"{self.year} {municipality}{town}", counts)
        self.towns[municipality].append((town, counts))

    def verify(self, grand_total: list[int]) -> None:
        for name in MUNICIPALITIES:
            town_sum = _sum([c for _, c in self.towns[name]])
            # 2017 年以降の CSV は認知の無い町村の行を持たない
            if self.municipality_totals.get(name, [0] * N_COUNTS) != town_sum:
                raise ValueError(f"{self.year} {name}: 町丁字の合計が区市町村計と合わない")
        outside = _sum(list(self.other_rows.values()))
        all_towns = _sum([c for rows in self.towns.values() for _, c in rows])
        if [a + b for a, b in zip(all_towns, outside)] != grand_total:
            raise ValueError(f"{self.year}: 町丁字と町丁字外の行の合計が合計の行と合わない")

    def rows(self) -> list[list]:
        out = []
        for name, (code, official) in MUNICIPALITIES.items():
            for town, counts in self.towns[name]:
                out.append([self.year, code, official, town, *counts])
        return out


def _parse_csv(content: bytes, year: int) -> _Year:
    reader = csv.reader(io.StringIO(content.decode("cp932")))
    header = next(reader)
    if header != ["市区町丁"] + [name for name, _ in COUNT_COLUMNS]:
        raise ValueError(f"{year}: CSV の見出しが想定と違う: {header}")

    data = _Year(year)
    grand_total = None
    region_totals = 0
    for row in reader:
        label, counts = _label(row[0]), [_count(v) for v in row[1:]]
        if label == "合計":
            grand_total = counts
        elif label in ("２３区計", "多摩地区・島部計"):
            region_totals += 1
        elif label in NON_TOWN_ROWS:
            data.other_rows[label] = counts
        elif label.endswith("計") and label[:-1] in MUNICIPALITIES:
            data.municipality_totals[label[:-1]] = counts
        elif label in MUNICIPALITIES and (label in data.municipality_totals or not any(counts)):
            # 2023 年以降は末尾に区市町村計の再掲がある。町丁字の行と計の行より後に来る
            if counts != data.municipality_totals.get(label, [0] * N_COUNTS):
                raise ValueError(f"{year} {label}: 末尾の区市町村計が計の行と合わない")
        else:
            prefix = next((p for p in MUNICIPALITY_PREFIXES if label.startswith(p)), None)
            if prefix is None:
                raise ValueError(f"{year}: 区市町村名で始まらない行: {label!r}")
            data.add_town(prefix, label[len(prefix):], counts)
    if grand_total is None or region_totals != 2:
        raise ValueError(f"{year}: 合計・地域計の行が揃っていない")
    data.verify(grand_total)
    return data


def _excel_sheets(content: bytes, filename: str) -> dict[str, list[list]]:
    """シート名 -> セル値の行リスト。xls と xlsx の差をここで吸収する。"""
    if filename.endswith(".xlsx"):
        book = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        return {ws.title: [list(r) for r in ws.iter_rows(values_only=True)] for ws in book.worksheets}
    book = xlrd.open_workbook(file_contents=content)
    return {
        s.name: [[s.cell_value(r, c) for c in range(s.ncols)] for r in range(s.nrows)]
        for s in book.sheets()
    }


def _label(value) -> str:
    return "" if value is None else str(value).strip().replace("　", "")


def _parse_excel(content: bytes, year: int, filename: str) -> _Year:
    sheets = _excel_sheets(content, filename)
    if set(sheets) != set(MUNICIPALITIES) | {EXCEL_SUMMARY_SHEET}:
        raise ValueError(f"{year}: シート構成が想定と違う: {sorted(set(sheets) ^ set(MUNICIPALITIES))}")

    # 区市町村計は最終シートから取る。認知の無い町村はシートに町丁字の行も計の行も無い
    data = _Year(year)
    grand_total = None
    for row in sheets[EXCEL_SUMMARY_SHEET][EXCEL_FIRST_DATA_ROW:]:
        label = _label(row[0])
        if label in MUNICIPALITIES:
            data.municipality_totals[label] = [_count(v) for v in row[1:N_COUNTS + 1]]
        elif label in NON_TOWN_ROWS:
            data.other_rows[label] = [_count(v) for v in row[1:N_COUNTS + 1]]
        elif label == "合計":
            grand_total = [_count(v) for v in row[1:N_COUNTS + 1]]
    if grand_total is None:
        raise ValueError(f"{year}: 最終シートに合計の行が無い")

    for name in MUNICIPALITIES:
        rows = sheets[name]
        if f"{year}年" not in "".join(_label(v) for v in rows[2]):
            raise ValueError(f"{year} {name}: シートの対象年が想定と違う")
        if _label(rows[6][3]) != "強盗" or _label(rows[6][N_COUNTS]) != "その他刑法犯":
            raise ValueError(f"{year} {name}: 列の見出しが想定と違う")
        for row in rows[EXCEL_FIRST_DATA_ROW:]:
            label = _label(row[0])
            if not label:
                continue
            counts = [_count(v) for v in row[1:N_COUNTS + 1]]
            if label == f"{name}計":
                if counts != data.municipality_totals.get(name):
                    raise ValueError(f"{year} {name}: シートの計が最終シートと合わない")
                break
            if not label.startswith(name):
                raise ValueError(f"{year} {name}: 区市町村名で始まらない行: {label!r}")
            data.add_town(name, label[len(name):], counts)

    data.verify(grand_total)
    return data


def download_and_normalize(csv_path: Path) -> int:
    rows = []
    for year, filename in FILES.items():
        content = _fetch(BASE_URL + filename)
        if filename.endswith(".csv"):
            data = _parse_csv(content, year)
        else:
            data = _parse_excel(content, year, filename)
        year_rows = data.rows()
        print(f"  {year}: {len(year_rows)} rows")
        rows.extend(year_rows)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_COLUMNS)
        writer.writerows(rows)
    return len(rows)
