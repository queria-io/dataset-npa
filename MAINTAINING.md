# 保守

## データ更新手順

main.py が警察庁の公開 CSV（本票、Shift-JIS）と各府県警の犯罪発生情報 CSV、犯罪統計資料の CSV と特殊詐欺の統計の Excel、
警視庁の町丁別認知件数の Excel / CSV を取得して UTF-8 へ正規化し、dbt build で各テーブルを再生成する。ビルドは `bash scripts/build.sh` で実行する（Queria に公開する）。
