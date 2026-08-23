"""都道府県警察 犯罪オープンデータ（犯罪発生情報）の取得・整形。

各都道府県警察が警察庁標準様式で公開する犯罪発生情報（窃盗の街頭犯罪7手口、
町丁目単位・1認知件1レコード）を取得し、単一の UTF-8 CSV へ正規化する。
発見起点は警察庁「犯罪オープンデータ リンク集」で、一次提供元は各都道府県警察。

対象は利用規約で商用利用・再配布可を確認済みの県のみ
（CC BY / 政府標準利用規約 第2.0版 準拠 / 公共データ利用規約 PDL1.0）。

県によってエンコーディング（UTF-8 BOM / Shift-JIS）と区切り（カンマ/タブ）が
混在するためファイル単位で自動判定する。列構成は手口により異なる標準様式
（共通10列 + 手口別列）のため、全手口の和集合スキーマへ揃え無い列は空にする。
"""

import csv
import http.client
import io
import time
import urllib.error
import urllib.request
from pathlib import Path

# 対象年（各県警の公開年別ファイル）。現在は令和6年で県横断比較できるよう統一。
# 将来は SOURCES に年別 URL を追加して拡張する。
DATA_YEAR = 2024

# BODIK (data.bodik.jp) は短間隔の連続アクセスを 403 で一時ブロックするため控えめにする
REQUEST_INTERVAL_SEC = 2.0

# 9 提供元から 60 ファイルを順に取るため、1 本の取りこぼしで全体が落ちる。
# 接続断とタイムアウトは間を空けて取り直す
FETCH_ATTEMPTS = 3
FETCH_BACKOFF_SEC = 5.0

# 原ファイル列名 -> 正規化列名。手口により存在する列が異なる（和集合）。
COLUMN_MAP = {
    "罪名": "crime_name",
    "手口": "modus",
    "管轄警察署（発生地）": "police_station",
    "管轄交番・駐在所（発生地）": "police_box",
    "市区町村コード（発生地）": "city_code",
    "都道府県（発生地）": "prefecture",
    "市区町村（発生地）": "city",
    "町丁目（発生地）": "town",
    "発生年月日（始期）": "occurred_date_raw",
    "発生時（始期）": "occurred_hour_raw",
    "発生場所": "location",
    "発生場所の詳細": "location_detail",
    "被害者の性別": "victim_gender",
    "被害者の年齢": "victim_age",
    "被害者の職業": "victim_occupation",
    "現金被害の有無": "cash_damage",
    "施錠関係": "lock_status",
    "盗難防止装置の有無": "anti_theft_device",
    "現金以外の主な被害品": "stolen_property",
}

OUTPUT_COLUMNS = [*COLUMN_MAP.values(), "source_prefecture", "data_year"]

_OSAKA = "https://www.police.pref.osaka.lg.jp/material/files/group/2"
_AICHI = "https://www.pref.aichi.jp/police/anzen/toukei/opendata/seian-s/images"
_KANAGAWA = "https://www.police.pref.kanagawa.jp/assets/entry"
_CHIBA = "https://www.police.pref.chiba.jp/content/common"
_BODIK = "https://data.bodik.jp/dataset"

_MODUS = ("hittakuri", "syazyounerai", "buhinnerai", "zidouhanbaikinerai",
          "zidousyatou", "ootobaitou", "zitensyatou")

# 県警別・手口別の年別 CSV。キーは手口スラッグ（警察庁リンク集の各県共通命名）。
# BODIK 掲載県（栃木・京都・佐賀・宮崎・鹿児島）はリソース URL が UUID 固定。
SOURCES: list[tuple[str, int, dict[str, str]]] = [
    ("栃木県", 2024, {
        "hittakuri": f"{_BODIK}/2bbcd73a-ac37-4a26-9a23-fcc72a5cfdd4/resource/73c74380-78c7-4ca6-a68c-2d0a0022dbee/download/d0110_2024_tochigi_2024hittakuri_07001.csv",
        "syazyounerai": f"{_BODIK}/4467d71d-90dd-40d1-968b-589c019aa3a6/resource/0bbb38bb-223d-453e-b999-4e542b7c3fa1/download/d0110_2024_tochigi_2024syazyounerai_07002.csv",
        "buhinnerai": f"{_BODIK}/4ae3fac3-e563-4680-b108-ca85040cf4dc/resource/acb39200-3a1d-433a-9e86-bba3d04cb1fe/download/d0110_2024_tochigi_2024buhinnerai_07003.csv",
        "zidouhanbaikinerai": f"{_BODIK}/c4a01778-5bdd-4914-819a-7a38a9b6ed2c/resource/e5dfc6c5-c63a-4909-9753-cc957fc7abdd/download/d0110_2024_tochigi_2024zidouhanbaikinerai_07004.csv",
        "zidousyatou": f"{_BODIK}/d54a0f04-4734-41a1-a4fe-23519b434340/resource/9de3c2f1-fa0a-4c7f-8bbe-3563128afb89/download/d0110_2024_tochigi_2024zidousyatou_07005.csv",
        "ootobaitou": f"{_BODIK}/f62f46eb-9809-4611-ad37-9f05569f1264/resource/e9bc2467-69d9-43ac-9ff7-922b2d8863d4/download/d0110_2024_tochigi_2024ootobaitou_07006.csv",
        "zitensyatou": f"{_BODIK}/93627019-71d4-4ce9-9473-342e6faa7ac3/resource/716a26c5-551b-415d-be85-643e83d71e32/download/d0110_2024_tochigi_2024zitensyatou_07007.csv",
    }),
    # 千葉県はファイル差し替え時に URL の連番が振り直され、旧番号は 404 になる。
    ("千葉県", 2024, {
        "hittakuri": f"{_CHIBA}/000074763.csv",
        "syazyounerai": f"{_CHIBA}/000074764.csv",
        "buhinnerai": f"{_CHIBA}/000074765.csv",
        "zidouhanbaikinerai": f"{_CHIBA}/000074766.csv",
        "zidousyatou": f"{_CHIBA}/000074767.csv",
        "ootobaitou": f"{_CHIBA}/000074768.csv",
        "zitensyatou": f"{_CHIBA}/000074769.csv",
    }),
    ("神奈川県", 2024, {
        m: f"{_KANAGAWA}/kanagawa_2024{m}.csv"
        for m in _MODUS
    }),
    ("愛知県", 2024, {
        m: f"{_AICHI}/aichi-2024{m}.csv"
        for m in _MODUS
    }),
    ("京都府", 2024, {
        "hittakuri": f"{_BODIK}/6a5f0b5c-667e-4a06-bbb8-6d191a5b1179/resource/a0827686-62e9-4d24-be45-aab159fb78f6/download/kyoto_2024hittakuri.csv",
        "syazyounerai": f"{_BODIK}/6a5f0b5c-667e-4a06-bbb8-6d191a5b1179/resource/34da31da-0b46-4c60-b65d-c04582a04533/download/kyoto_2024syajounerai.csv",
        "buhinnerai": f"{_BODIK}/6a5f0b5c-667e-4a06-bbb8-6d191a5b1179/resource/0e48cfca-20bc-4816-a986-5a20e49725d9/download/kyoto_2024buhinnerai.csv",
        "zidouhanbaikinerai": f"{_BODIK}/6a5f0b5c-667e-4a06-bbb8-6d191a5b1179/resource/88a0cfe0-3305-4ccb-8171-e945378ccbe3/download/kyoto_2024zidouhannbaikinerai.csv",
        "zidousyatou": f"{_BODIK}/6a5f0b5c-667e-4a06-bbb8-6d191a5b1179/resource/ae6d0336-504c-48ce-a3ed-aeed03bb3623/download/kyoto_2024zidousyatou.csv",
        "ootobaitou": f"{_BODIK}/6a5f0b5c-667e-4a06-bbb8-6d191a5b1179/resource/f8e91ffc-d2ea-4c95-ae0e-e6e5e2b886b3/download/kyoto_2024ootobaitou.csv",
        "zitensyatou": f"{_BODIK}/6a5f0b5c-667e-4a06-bbb8-6d191a5b1179/resource/625c707a-e776-4911-9d84-89f6f68c5415/download/kyoto_2024zitensyatou.csv",
    }),
    ("大阪府", 2024, {
        m: f"{_OSAKA}/osaka_2024{m}.csv"
        for m in _MODUS
    }),
    ("佐賀県", 2024, {
        "hittakuri": f"{_BODIK}/cec6d1da-8160-4967-bb9a-98092aa827e6/resource/61de0a68-0f01-4841-8473-7bdbb1ac5a2e/download/saga_2024hittakuri.csv",
        "syazyounerai": f"{_BODIK}/cec6d1da-8160-4967-bb9a-98092aa827e6/resource/cd1e7224-4c28-49a2-9e69-5d9cbdfab8dd/download/saga_2024syazyounerai.csv",
        "buhinnerai": f"{_BODIK}/cec6d1da-8160-4967-bb9a-98092aa827e6/resource/22bcdfdb-0918-4464-b28a-1df7508808a0/download/saga_2024buhinnerai.csv",
        "zidouhanbaikinerai": f"{_BODIK}/cec6d1da-8160-4967-bb9a-98092aa827e6/resource/3cab17f2-137f-4f6f-8511-48fb67f0fa18/download/saga_2024zidouhanbaikinerai.csv",
        "zidousyatou": f"{_BODIK}/cec6d1da-8160-4967-bb9a-98092aa827e6/resource/e2f955d1-181c-44ee-bf7b-392a0738b0b7/download/saga_2024zidousyatou.csv",
        "ootobaitou": f"{_BODIK}/cec6d1da-8160-4967-bb9a-98092aa827e6/resource/48283b13-e4d7-427c-b2be-a792e671be3f/download/saga_2024ootobaitou.csv",
        "zitensyatou": f"{_BODIK}/cec6d1da-8160-4967-bb9a-98092aa827e6/resource/966353ea-79e2-4485-9643-cbb16c08835a/download/saga_2024zitensyatou.csv",
    }),
    ("宮崎県", 2024, {
        "hittakuri": f"{_BODIK}/a7c23d02-7ba8-4685-a09f-576a6cc7054f/resource/01a13084-2ebc-4874-b736-0d1cacd27fa0/download/miyazaki_2024hittakuri.csv",
        "syazyounerai": f"{_BODIK}/a7c23d02-7ba8-4685-a09f-576a6cc7054f/resource/f867417a-e6af-4f36-8140-474c68f9cc15/download/miyazaki_2024syazyounerai.csv",
        "buhinnerai": f"{_BODIK}/a7c23d02-7ba8-4685-a09f-576a6cc7054f/resource/38d10bd0-802c-4145-a470-d4c82204189a/download/miyazaki_2024buhinnerai.csv",
        "zidouhanbaikinerai": f"{_BODIK}/a7c23d02-7ba8-4685-a09f-576a6cc7054f/resource/da76ffb8-f4c1-40ff-aa97-52b5dbe981f3/download/miyazaki_2024zidouhanbaikinerai.csv",
        "zidousyatou": f"{_BODIK}/a7c23d02-7ba8-4685-a09f-576a6cc7054f/resource/b7736020-6f5e-49d9-8625-1bf0be2d8fa7/download/miyazaki_2024zidousyatou.csv",
        "ootobaitou": f"{_BODIK}/a7c23d02-7ba8-4685-a09f-576a6cc7054f/resource/dbc8dd3e-0220-4708-85b2-472818005b17/download/miyazaki_2024ootobaitou.csv",
        "zitensyatou": f"{_BODIK}/a7c23d02-7ba8-4685-a09f-576a6cc7054f/resource/93f92c26-7d12-4e86-989b-77b73cfcbd94/download/miyazaki_2024zitensyatou.csv",
    }),
    ("鹿児島県", 2024, {
        "hittakuri": f"{_BODIK}/d7bc06be-ac8b-4d4a-8108-9f25544276c0/resource/4dc2ad6f-87d9-4462-8351-aed7ef7ce87d/download/hittakuri.csv",
        "syazyounerai": f"{_BODIK}/d7bc06be-ac8b-4d4a-8108-9f25544276c0/resource/d1595af4-045c-4f30-a3b9-9cf5208f3c92/download/syajounerai.csv",
        "buhinnerai": f"{_BODIK}/d7bc06be-ac8b-4d4a-8108-9f25544276c0/resource/31ed0893-0188-4b3a-8382-4f096d2904e2/download/buhinnnerai.csv",
        "zidouhanbaikinerai": f"{_BODIK}/d7bc06be-ac8b-4d4a-8108-9f25544276c0/resource/80962404-8898-48e7-a8db-2a32f8bc02a8/download/jidouhannbaikinerai.csv",
        "zidousyatou": f"{_BODIK}/d7bc06be-ac8b-4d4a-8108-9f25544276c0/resource/a7aad9d9-aa71-43f1-8011-be85dba97063/download/jidousyatou.csv",
        "ootobaitou": f"{_BODIK}/d7bc06be-ac8b-4d4a-8108-9f25544276c0/resource/08ed7034-db06-4690-9402-2e49df7d845d/download/o-tobaitou.csv",
        "zitensyatou": f"{_BODIK}/d7bc06be-ac8b-4d4a-8108-9f25544276c0/resource/da75606e-cf9c-42dc-9519-63cf08c06d18/download/jitennsyatou.csv",
    }),
]


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(1, FETCH_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError) as exc:
            # 404 のような恒久的な応答は取り直しても変わらない。URL の更新が要る
            if isinstance(exc, urllib.error.HTTPError):
                raise
            if attempt == FETCH_ATTEMPTS:
                raise
            print(f"  retry {attempt}/{FETCH_ATTEMPTS - 1}: {url} ({exc})")
            time.sleep(FETCH_BACKOFF_SEC * attempt)
    raise AssertionError("unreachable")


def _decode_and_split(raw: bytes) -> list[list[str]]:
    """エンコーディングと区切り文字をファイル単位で判定し、行リストへ分解する。

    大阪府は同一年内でも UTF-8 BOM/カンマ区切りと Shift-JIS/タブ区切りが
    ファイルごとに混在する（拡張子はいずれも .csv）。
    """
    if raw.startswith(b"\xef\xbb\xbf"):
        text = raw.decode("utf-8-sig")
    else:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("cp932")
    first_line = text.splitlines()[0]
    delimiter = "\t" if first_line.count("\t") > first_line.count(",") else ","
    return list(csv.reader(io.StringIO(text), delimiter=delimiter))


def _normalize(rows: list[list[str]], prefecture: str, year: int) -> list[list[str]]:
    """標準様式の可変列を和集合スキーマへ正規化する。存在しない列は空。"""
    header = [h.strip() for h in rows[0]]
    index = {name: header.index(name) for name in COLUMN_MAP if name in header}
    unknown = [h for h in header if h not in COLUMN_MAP]
    if unknown:
        raise ValueError(f"{prefecture}: 標準様式にない列 {unknown}")

    out: list[list[str]] = []
    for row in rows[1:]:
        if not row or all(not cell.strip() for cell in row):
            continue
        values = [
            row[index[src]].strip() if src in index and index[src] < len(row) else ""
            for src in COLUMN_MAP
        ]
        out.append([*values, prefecture, str(year)])
    return out


def download_and_normalize(csv_path: Path) -> int:
    """全対象県・全手口を取得・正規化して 1 つの UTF-8 CSV に書き出し、行数を返す。"""
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    all_rows: list[list[str]] = []
    for prefecture, year, urls in SOURCES:
        pref_count = 0
        for modus, url in urls.items():
            rows = _decode_and_split(_fetch(url))
            normalized = _normalize(rows, prefecture, year)
            pref_count += len(normalized)
            all_rows.extend(normalized)
            time.sleep(REQUEST_INTERVAL_SEC)
        print(f"  {prefecture} {year}: {pref_count} rows")

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(OUTPUT_COLUMNS)
        writer.writerows(all_rows)
    return len(all_rows)
