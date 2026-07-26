"""警察庁関連オープンデータの取得 + dbt ビルド。

1. honhyo: 警察庁公開の年別本票 CSV を取得し、緯度経度付きの交通事故レコードを
           正規化した UTF-8 CSV へ整形する。
2. crime:  都道府県警察公開の犯罪発生情報（街頭犯罪7手口）を取得し、
           統合した UTF-8 CSV へ整形する。
3. dbt:    dbt ビルド。
"""

import logging
from pathlib import Path

from dbt.cli.main import dbtRunner

import crime
import honhyo

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("pipelines")

WORK_DIR = Path(".queria")
CSV_PATH = WORK_DIR / "npa_honhyo.csv"
CRIME_CSV_PATH = WORK_DIR / "npa_crime.csv"


def dbt_build() -> None:
    dbt = dbtRunner()
    for cmd in (["deps"], ["run"], ["docs", "generate"]):
        result = dbt.invoke(cmd)
        if not result.success:
            raise SystemExit(f"dbt {cmd[0]} failed")


def main() -> None:
    WORK_DIR.mkdir(exist_ok=True)

    logger.info("1/3: honhyo (交通事故 本票)")
    rows = honhyo.download_and_normalize(CSV_PATH)
    logger.info(f"  npa_honhyo.csv: {rows} rows")

    logger.info("2/3: crime (犯罪発生情報)")
    rows = crime.download_and_normalize(CRIME_CSV_PATH)
    logger.info(f"  npa_crime.csv: {rows} rows")

    logger.info("3/3: dbt build")
    dbt_build()


if __name__ == "__main__":
    main()
