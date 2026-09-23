"""警察庁関連オープンデータの取得 + dbt ビルド。

1. honhyo: 警察庁公開の年別本票 CSV を取得し、緯度経度付きの交通事故レコードを
           正規化した UTF-8 CSV へ整形する。
2. crime:  都道府県警察公開の犯罪発生情報（街頭犯罪7手口）を取得し、
           統合した UTF-8 CSV へ整形する。
3. crime_stats: 警察庁 犯罪統計資料（確定値）の都道府県別表を取得し、
           罪種×地域の縦持ち CSV へ整形する。
4. dbt:    dbt ビルド。
"""

import logging
from pathlib import Path

from dbt.cli.main import dbtRunner

import crime
import crime_stats
import honhyo

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("pipelines")

WORK_DIR = Path(".queria")
CSV_PATH = WORK_DIR / "npa_honhyo.csv"
CRIME_CSV_PATH = WORK_DIR / "npa_crime.csv"
CRIME_STATS_CSV_PATH = WORK_DIR / "npa_crime_stats.csv"


def dbt_build() -> None:
    dbt = dbtRunner()
    for cmd in (["deps"], ["run"], ["docs", "generate"]):
        result = dbt.invoke(cmd)
        if not result.success:
            raise SystemExit(f"dbt {cmd[0]} failed")


def main() -> None:
    WORK_DIR.mkdir(exist_ok=True)

    logger.info("1/4: honhyo (交通事故 本票)")
    rows = honhyo.download_and_normalize(CSV_PATH)
    logger.info(f"  npa_honhyo.csv: {rows} rows")

    logger.info("2/4: crime (犯罪発生情報)")
    rows = crime.download_and_normalize(CRIME_CSV_PATH)
    logger.info(f"  npa_crime.csv: {rows} rows")

    logger.info("3/4: crime_stats (犯罪統計資料)")
    rows = crime_stats.download_and_normalize(CRIME_STATS_CSV_PATH)
    logger.info(f"  npa_crime_stats.csv: {rows} rows")

    logger.info("4/4: dbt build")
    dbt_build()


if __name__ == "__main__":
    main()
