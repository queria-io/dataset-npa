"""警察庁 交通事故統計情報の取得 + dbt ビルド。

1. honhyo: 警察庁公開の年別本票 CSV を取得し、緯度経度付きの交通事故レコードを
           正規化した UTF-8 CSV へ整形する。
2. dbt:    dbt ビルド。
"""

import logging
from pathlib import Path

from dbt.cli.main import dbtRunner

from honhyo import download_and_normalize

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("pipelines")

FDL_DIR = Path(".fdl")
CSV_PATH = FDL_DIR / "npa_honhyo.csv"


def dbt_build() -> None:
    dbt = dbtRunner()
    for cmd in (["deps"], ["run"], ["docs", "generate"]):
        result = dbt.invoke(cmd)
        if not result.success:
            raise SystemExit(f"dbt {cmd[0]} failed")


def main() -> None:
    FDL_DIR.mkdir(exist_ok=True)

    logger.info("1/2: honhyo (交通事故 本票)")
    rows = download_and_normalize(CSV_PATH)
    logger.info(f"  npa_honhyo.csv: {rows} rows")

    logger.info("2/2: dbt build")
    dbt_build()


if __name__ == "__main__":
    main()
