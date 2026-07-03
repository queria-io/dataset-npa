"""警察庁 交通事故統計情報（本票）の取得・整形。

警察庁が公開する年別の本票 CSV（Shift-JIS）を取得し、緯度経度を持つ
交通事故レコードを扱いやすい列だけに絞った UTF-8 CSV へ正規化する。

本票（honhyo）は死傷者を伴う交通事故を1件1レコードで収録する。列は年により
末尾に項目が追加されるが、ここで採用する中核列はどの年も同一の列名で存在するため、
ヘッダ名で列を選択して年をまたいで安定した正規化スキーマに揃える。
"""

import csv
import io
import urllib.request
from pathlib import Path

# 取得対象年（発生年ベースの年別ファイル）。
# 年別ファイルは発生年が混在する（前年12月分等）ため、跨ぎの重複を避けるべく
# 各ファイルは当該発生年のレコードのみ採用する。将来はここへ年を追加する。
HONHYO_YEARS = [2024]

BASE_URL = "https://www.npa.go.jp/publications/statistics/koutsuu/opendata"

# 原ファイル列名 -> 正規化列名。中核列のみを採用する。
COLUMN_MAP = {
    "都道府県コード": "prefecture_code",
    "警察署等コード": "police_station_code",
    "本票番号": "accident_number",
    "事故内容": "accident_type_code",
    "死者数": "fatalities",
    "負傷者数": "injuries",
    "市区町村コード": "city_code",
    "発生日時　　年": "occurred_year",
    "発生日時　　月": "occurred_month",
    "発生日時　　日": "occurred_day",
    "発生日時　　時": "occurred_hour",
    "発生日時　　分": "occurred_minute",
    "昼夜": "day_night_code",
    "天候": "weather_code",
    "地形": "terrain_code",
    "路面状態": "road_surface_code",
    "道路形状": "road_shape_code",
    "信号機": "traffic_signal_code",
    "事故類型": "accident_pattern_code",
    "曜日(発生年月日)": "day_of_week_code",
    "祝日(発生年月日)": "holiday_code",
    "地点　緯度（北緯）": "latitude_dms",
    "地点　経度（東経）": "longitude_dms",
}

OUTPUT_COLUMNS = list(COLUMN_MAP.values())


def _fetch_rows(year: int) -> list[dict]:
    """指定年の本票 CSV を取得し、Shift-JIS を UTF-8 に解して行辞書を返す。"""
    url = f"{BASE_URL}/{year}/honhyo_{year}.csv"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()
    text = raw.decode("cp932")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def _normalize(rows: list[dict], year: int) -> list[list[str]]:
    """中核列だけを取り出し、当該発生年のレコードのみへ絞る。"""
    out: list[list[str]] = []
    for row in rows:
        # 年別ファイルの跨ぎ重複を避けるため発生年で厳密に絞る
        if (row.get("発生日時　　年") or "").strip() != str(year):
            continue
        out.append([(row.get(src) or "").strip() for src in COLUMN_MAP])
    return out


def download_and_normalize(csv_path: Path) -> int:
    """全対象年を取得・正規化して 1 つの UTF-8 CSV に書き出し、行数を返す。"""
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    all_rows: list[list[str]] = []
    for year in HONHYO_YEARS:
        rows = _fetch_rows(year)
        all_rows.extend(_normalize(rows, year))

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_COLUMNS)
        writer.writerows(all_rows)

    return len(all_rows)
