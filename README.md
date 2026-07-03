## データ出典

[警察庁 交通事故統計情報のオープンデータ](https://www.npa.go.jp/publications/statistics/koutsuu/opendata/index_opendata.html)です。
死傷者を伴う交通事故を1件1レコードで収録し、発生日時・地点（緯度経度）・事故内容・天候・路面状態・
道路形状・事故類型などを持ちます。緯度経度を持つため地図上での事故分析（GIS）に利用できます。

## テーブル: traffic_accident

交通事故の発生地点（ポイント）です。警察庁が公開する年別の本票（honhyo）を取り込み、2024年（令和6年）
発生分を収録します。各種コードは警察庁「各種コード表」に基づき名称を付与します。

- accident_id: 事故識別子（VARCHAR、発生年・都道府県・警察署等・本票番号を連結した一意キー）
- prefecture_code: 都道府県コード（VARCHAR、警察の管轄区分。北海道は方面別に5分割。JIS コードとは異なる）
- prefecture: 都道府県（VARCHAR）
- police_station_code: 警察署等コード（VARCHAR）
- accident_number: 本票番号（VARCHAR）
- accident_type_code: 事故内容コード（VARCHAR、1=死亡、2=負傷）
- accident_type: 事故内容（VARCHAR、死亡／負傷）
- fatalities: 死者数（INTEGER、発生から24時間以内）
- injuries: 負傷者数（INTEGER）
- city_code: 市区町村コード（VARCHAR、警察独自の3桁コード。JIS 市区町村コードとは異なる）
- occurred_date: 発生日（DATE）
- occurred_at: 発生日時（TIMESTAMP、時分が不明の場合は NULL）
- occurred_year / occurred_month / occurred_day / occurred_hour / occurred_minute: 発生年月日時分（INTEGER）
- day_of_week_code / day_of_week: 曜日（VARCHAR）
- holiday_code / holiday: 祝日（VARCHAR、当日／前日／その他）
- day_night_code / day_night: 昼夜（VARCHAR、日の出・日の入り前後1時間の明暮を区別）
- weather_code / weather: 天候（VARCHAR、晴／曇／雨／霧／雪）
- terrain_code / terrain: 地形（VARCHAR、市街地（人口集中／その他）・非市街地の別）
- road_surface_code / road_surface: 路面状態（VARCHAR）
- road_shape_code / road_shape: 道路形状（VARCHAR、交差点・単路・踏切などの別）
- traffic_signal_code / traffic_signal: 信号機（VARCHAR、当事者が対面する信号機の作動状況）
- accident_pattern_code / accident_pattern: 事故類型（VARCHAR、人対車両・車両相互・車両単独・列車の別）
- latitude: 緯度（DOUBLE、北緯・十進度）
- longitude: 経度（DOUBLE、東経・十進度）
- geometry: 位置（GEOMETRY、緯度経度から生成した地点ポイント）

緯度経度は原典では度分秒を桁で連結した固定長文字列（緯度9桁 DDMMSSsss、経度10桁 DDDMMSSsss、
秒は小数3桁）で提供されるため、十進度へ変換したうえで geometry（ポイント）を生成しています。

年別ファイルには発生年の異なるレコード（前年12月分等）が少数混在するため、跨ぎの重複を避けるべく
各ファイルは当該発生年のレコードのみを採用します。過去年・補充票（当事者別）・高速票（高速道路）の
取り込みは将来の拡張余地です。

### データ更新手順

main.py が警察庁の公開 CSV（本票、Shift-JIS）を取得して UTF-8 の中核列へ正規化し、dbt build で
交通事故テーブルを再生成する。ビルドは `bash scripts/build.sh local` で実行する。

## ライセンス

警察庁ウェブサイトのコンテンツに準拠する[公共データ利用規約（第1.0版）（PDL1.0）](https://www.npa.go.jp/rules/index.html)に従う。

出典: 「交通事故統計情報のオープンデータ」（警察庁）（https://www.npa.go.jp/publications/statistics/koutsuu/opendata/index_opendata.html）を加工して作成。

Shift-JIS の年別本票 CSV を UTF-8 へ変換し、緯度経度の度分秒を十進度へ変換のうえ地点ポイントを生成する
加工、および各種コードへの名称付与を行っている。統計値そのものは改変していない。
