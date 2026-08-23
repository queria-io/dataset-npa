## データ出典

警察庁と都道府県警察が公開する犯罪・交通事故のオープンデータです。

- [警察庁 交通事故統計情報のオープンデータ](https://www.npa.go.jp/publications/statistics/koutsuu/opendata/index_opendata.html):
  死傷者を伴う交通事故を1件1レコードで収録し、発生日時・地点（緯度経度）・事故内容・天候・路面状態・
  道路形状・事故類型などを持ちます。緯度経度を持つため地図上での事故分析（GIS）に利用できます。
- 都道府県警察の犯罪発生情報（発見起点: [警察庁 犯罪オープンデータ リンク集](https://www.npa.go.jp/toukei/seianki/hanzaiopendatalink.html)）:
  各都道府県警察が警察庁標準様式で公開する街頭犯罪の認知情報を、1認知件1レコード・町丁目単位で収録します。

## スキーマ: main

### テーブル: traffic_accident

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

## スキーマ: crime

### テーブル: theft

都道府県警察が公開する犯罪発生情報です。窃盗のうち街頭犯罪7手口（ひったくり・車上ねらい・
部品ねらい・自動販売機ねらい・自動車盗・オートバイ盗・自転車盗）を1認知件1レコード・
町丁目単位で収録します。

現在は令和6年（2024年）分・13府県（青森・福島・栃木・埼玉・千葉・神奈川・愛知・京都・大阪・
徳島・佐賀・宮崎・鹿児島）を収録します。対象は利用規約で商用利用・再配布可を確認できた府県のみで、
他の都道府県・過去年の取り込みは将来の拡張余地です。

- crime_name: 罪名（VARCHAR、窃盗。一部に常習累犯窃盗）
- modus: 手口（VARCHAR、ひったくり／車上ねらい／部品ねらい／自動販売機ねらい／自動車盗／オートバイ盗／自転車盗）
- prefecture: 都道府県（VARCHAR、発生地。不明の場合は NULL）
- city_code: 市区町村コード（VARCHAR、JIS 市区町村コード6桁・チェックデジット付き。政令指定都市は区コード）
- city: 市区町村（VARCHAR、発生地）
- town: 町丁目（VARCHAR、発生地）
- occurred_date: 発生年月日・始期（DATE、「不明」は NULL。認知年より過去に遡ることがある）
- occurred_hour: 発生時・始期（INTEGER、0〜23。「不明」は NULL）
- location: 発生場所（VARCHAR、道路上・駐車（輪）場・一戸建住宅など）
- location_detail: 発生場所の詳細（VARCHAR、ひったくりには存在しない）
- police_station: 管轄警察署（VARCHAR、発生地）
- police_box: 管轄交番・駐在所（VARCHAR、発生地）
- victim_gender: 被害者の性別（VARCHAR、ひったくりのみ）
- victim_age: 被害者の年齢（VARCHAR、年代区分。ひったくり・自転車盗のみ）
- victim_occupation: 被害者の職業（VARCHAR、自転車盗のみ）
- cash_damage: 現金被害の有無（VARCHAR、ひったくり・車上ねらい・自動販売機ねらいのみ）
- lock_status: 施錠関係（VARCHAR、車上ねらい・自動車盗・オートバイ盗・自転車盗のみ）
- anti_theft_device: 盗難防止装置の有無（VARCHAR、自動車盗・オートバイ盗のみ）
- stolen_property: 現金以外の主な被害品（VARCHAR、部品ねらい・自動車盗・オートバイ盗のみ）
- source_prefecture: 公表元県警の都道府県（VARCHAR、発生地の都道府県とは別に常に値を持つ）
- data_year: データ対象年（INTEGER、公開データの対象年＝認知年。西暦）

列は警察庁標準様式（手口別の可変列）の和集合で、手口に存在しない列は NULL です。
県により先頭ゼロが欠落した市区町村コード（5桁）は6桁へ復元し、エンコーディング
（UTF-8 BOM / Shift-JIS）と区切り文字（カンマ／タブ）の混在はファイル単位で自動判定して
統合しています。発生地が不明のレコード（都道府県・市区町村コードが空）も原典どおり保持します。
発生地不明を空欄ではなく「日本国内のいずれかの場所」等の文言で表す県があるため、都道府県名でない
値は空欄と同じく NULL に寄せています。

## データ更新手順

main.py が警察庁の公開 CSV（本票、Shift-JIS）と各府県警の犯罪発生情報 CSV を取得して UTF-8 へ
正規化し、dbt build で各テーブルを再生成する。ビルドは `bash scripts/build.sh` で実行する（Queria に公開する）。

## ライセンス

交通事故統計情報は、警察庁ウェブサイトのコンテンツに準拠する
[公共データ利用規約（第1.0版）（PDL1.0）](https://www.npa.go.jp/rules/index.html)に従う。

犯罪発生情報は、公表元の各都道府県警察の利用規約に従う。いずれも商用利用・再配布可
（出典記載が条件）を確認済み。

- 青森県警察: [公共データ利用規約（第1.0版）（PDL1.0）](https://www.police.pref.aomori.jp/seianbu/seian_kikaku/hanyoku/hanyoku_opendate.html)
- 福島県警察: [福島県警察ホームページ利用規約（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.fukushima.jp/16.kiyaku/16.kiyaku.html)
- 栃木県警察: [CC BY 2.1 JP](https://data.bodik.jp/organization/090000)
- 埼玉県警察: [埼玉県警察ホームページ利用規約（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.saitama.lg.jp/riyokiyaku.html)
- 千葉県警察: [千葉県警察ウェブサイト利用規約（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.chiba.jp/kohoka/help_point01.html)
- 神奈川県警察: [神奈川県警察利用ルール（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.kanagawa.jp/tokei/hanzai_tokei/mesd0146.html)
- 愛知県警察: [公共データ利用規約（第1.0版）（PDL1.0）](https://www.pref.aichi.jp/police/anzen/toukei/opendata/seian-s/crimeopendata.html)
- 京都府警察: [CC BY 4.0](https://data.bodik.jp/organization/260002)
- 大阪府警察: [大阪府警察公表データの利用ルール（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.osaka.lg.jp/seikatsu/9260.html)
- 徳島県警察: [徳島県警察ホームページ利用規約（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.tokushima.jp/28opendata/index.html)
- 佐賀県警察: [CC BY 4.0](https://data.bodik.jp/dataset/410004_hanzaijyouhou)
- 宮崎県警察: [CC BY 4.0](https://data.bodik.jp/dataset/450006_1069)
- 鹿児島県警察: [CC BY 4.0（オープンデータ利用規約併記）](https://data.bodik.jp/dataset/460001_hanzaihassei_2024)

出典:
「交通事故統計情報のオープンデータ」（警察庁）（https://www.npa.go.jp/publications/statistics/koutsuu/opendata/index_opendata.html）、
および青森県警察・福島県警察・栃木県警察・埼玉県警察・千葉県警察・神奈川県警察・愛知県警察・
京都府警察・大阪府警察・徳島県警察・佐賀県警察・宮崎県警察・鹿児島県警察の犯罪発生情報
（犯罪オープンデータ）を加工して作成。

Shift-JIS の CSV を UTF-8 へ変換し、交通事故は緯度経度の度分秒を十進度へ変換のうえ地点ポイントを
生成する加工と各種コードへの名称付与、犯罪発生情報は手口別の可変列を和集合スキーマへ統合する
加工を行っている。統計値そのものは改変していない。
