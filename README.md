# 警察庁・都道府県警察 犯罪・交通事故統計

警察庁・警視庁・都道府県警察が公開する交通事故と犯罪のオープンデータを、SQL で検索・集計できるテーブルにしたデータセットです。交通事故は 1 件ごとの地点、犯罪は町丁目単位の発生情報と都道府県別・全国の統計を持ちます。

## 出典と利用条件

- [警察庁 交通事故統計情報のオープンデータ](https://www.npa.go.jp/publications/statistics/koutsuu/opendata/index_opendata.html)
- 都道府県警察の犯罪発生情報（[警察庁 犯罪オープンデータ リンク集](https://www.npa.go.jp/toukei/seianki/hanzaiopendatalink.html)から各府県警の公開ページへ）
- [警察庁 犯罪統計](https://www.npa.go.jp/publications/statistics/sousa/statistics.html)（政府統計の総合窓口 e-Stat 掲載の CSV）
- [警察庁 特殊詐欺の認知・検挙状況等について](https://www.npa.go.jp/publications/statistics/sousa/sagi.html)
- [警視庁 区市町村の町丁別、罪種別及び手口別認知件数](https://www.keishicho.metro.tokyo.lg.jp/about_mpd/jokyo_tokei/jokyo/ninchikensu.html)


交通事故統計情報と特殊詐欺の統計は、警察庁ウェブサイトのコンテンツに準拠する
[公共データ利用規約（第1.0版）（PDL1.0）](https://www.npa.go.jp/rules/index.html)に従います。

犯罪統計資料は、[政府統計の総合窓口（e-Stat）利用規約（政府標準利用規約（第2.0版）準拠）](https://www.e-stat.go.jp/terms-of-use)に従います。

警視庁の町丁別認知件数は、[東京都オープンデータカタログサイト](https://catalog.data.metro.tokyo.lg.jp/dataset/t000022d0000100001)に
掲載された [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja) に従います。

犯罪発生情報は、公表元の各都道府県警察の利用規約に従います。いずれも商用利用・再配布可
（出典記載が条件）を確認しています。

- 青森県警察: [公共データ利用規約（第1.0版）（PDL1.0）](https://www.police.pref.aomori.jp/seianbu/seian_kikaku/hanyoku/hanyoku_opendate.html)
- 福島県警察: [福島県警察ホームページ利用規約（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.fukushima.jp/16.kiyaku/16.kiyaku.html)
- 栃木県警察: [CC BY 2.1 JP](https://data.bodik.jp/organization/090000)
- 埼玉県警察: [埼玉県警察ホームページ利用規約（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.saitama.lg.jp/riyokiyaku.html)
- 千葉県警察: [千葉県警察ウェブサイト利用規約（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.chiba.jp/kohoka/help_point01.html)
- 神奈川県警察: [神奈川県警察利用ルール（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.kanagawa.jp/tokei/hanzai_tokei/mesd0146.html)
- 京都府警察: [CC BY 4.0](https://data.bodik.jp/organization/260002)
- 大阪府警察: [大阪府警察公表データの利用ルール（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.osaka.lg.jp/seikatsu/9260.html)
- 徳島県警察: [徳島県警察ホームページ利用規約（政府標準利用規約（第2.0版）準拠）](https://www.police.pref.tokushima.jp/28opendata/index.html)
- 佐賀県警察: [CC BY 4.0](https://data.bodik.jp/dataset/410004_hanzaijyouhou)
- 宮崎県警察: [CC BY 4.0](https://data.bodik.jp/dataset/450006_1069)
- 鹿児島県警察: [CC BY 4.0（オープンデータ利用規約併記）](https://data.bodik.jp/dataset/460001_hanzaihassei_2024)

## テーブル

| テーブル | 内容 | 行数 |
| --- | --- | ---: |
| `main.traffic_accident` | 人身事故の発生地点（1 件 1 行、緯度経度つき、2024 年） | 282,376 |
| `crime.theft` | 街頭犯罪 7 手口の発生情報（1 認知件 1 行、町丁目単位、12 府県の 2024 年） | 98,794 |
| `crime.prefecture_crime` | 都道府県別・罪種別の認知件数・検挙件数・検挙人員（2020〜2025 年） | 5,640 |
| `crime.special_fraud` | 特殊詐欺の全国の手口別・月別の認知件数・被害額（2020 年 1 月から） | 1,072 |
| `crime.tokyo_town_crime` | 東京都の町丁字別・罪種別・手口別の認知件数（2009 年から） | 87,273 |
| `code.prefecture` | 交通事故統計の都道府県コード（警察）と JIS の都道府県コードの対応 | 51 |

## 使い方

全国の刑法犯の認知件数と検挙率の推移を出す:

```sql
SELECT year,
       sum(recognized_cases) AS cases,
       round(100.0 * sum(cleared_cases) / sum(recognized_cases), 1) AS clearance_rate
FROM npa.crime.prefecture_crime
WHERE crime_type = '刑法犯総数'
GROUP BY ALL
ORDER BY year;
```

## 注意

- `crime.theft` は 12 府県（青森・福島・栃木・埼玉・千葉・神奈川・京都・大阪・徳島・佐賀・宮崎・鹿児島）だけで、全国の件数には使えません。府県間で件数を比べることもできません。全国を同じ定義で比べるときは `crime.prefecture_crime` を使ってください。東京都の町丁目単位の犯罪は `crime.tokyo_town_crime` にあります
- 交通事故を市区町村で他のテーブルと結合するときは `lg_code`（6 桁）を使います。`prefecture_code` は警察独自のコード（北海道は方面別に 5 分割）で、`city_code` は市区町村の部分の 3 桁だけなので、2 つを連結しても JIS のコードになりません。犯罪のテーブルの `city_code` は 6 桁の全国地方公共団体コードです
- 罪種・手口には包含関係や合計の行があります（侵入盗は窃盗犯の内数、`modus` が「特殊詐欺」の行は全手口の合計、`total` は罪種の計の合計）。罪種や手口をまたいで合計しないでください
- 交通事故は死傷者を伴う人身事故だけで、物損事故は含みません。死者は発生から 24 時間以内の死者です

## main.traffic_accident

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
- city_code: 市区町村コード（VARCHAR、標準地域コードの市区町村の部分の 3 桁。都道府県の部分を含まない）
- lg_code: 全国地方公共団体コード（VARCHAR、6 桁・検査数字付き。発生地の市区町村で、政令指定都市は区）
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

`lg_code` は、警察の都道府県コードを「各種コード表」の都道府県名から JIS X 0401 の 2 桁に変換し（北海道の 5 方面はどれも `01`）、
`city_code` の 3 桁と連結して検査数字を付けたものです。都道府県コードの対応は `code.prefecture` で引けます。「各種コード表」によると `city_code` は総務省の標準地域コードで、
年の途中で市町村の合併などがあった場合はその年の間は従前のコードを使います。そのため `lg_code` は発生年の時点のコードです。

緯度経度は原典では度分秒を桁で連結した固定長文字列（緯度9桁 DDMMSSsss、経度10桁 DDDMMSSsss、
秒は小数3桁）で提供されるため、十進度へ変換したうえで geometry（ポイント）を生成しています。

年別ファイルには発生年の異なるレコード（前年12月分等）が少数混在するため、年をまたぐ重複を避けるため、
各ファイルからは当該発生年のレコードだけを採っています。補充票（当事者別）・高速票（高速道路）は収録しません。

## code.prefecture

交通事故統計の都道府県コード（警察の管轄区分）と、JIS X 0401 の都道府県コードの対応表です。
`main.traffic_accident` の `lg_code` はこの対応で作っています。

- prefecture_code: 都道府県コード（VARCHAR、交通事故統計の 2 桁。北海道は方面別に 10〜14）
- prefecture: 都道府県（VARCHAR、「各種コード表」の名称）
- jis_prefecture_code: 都道府県コード（VARCHAR、JIS X 0401 の 2 桁）

## crime.theft

都道府県警察が公開する犯罪発生情報です。窃盗のうち街頭犯罪7手口（ひったくり・車上ねらい・
部品ねらい・自動販売機ねらい・自動車盗・オートバイ盗・自転車盗）を1認知件1レコード・
町丁目単位で収録します。

現在は令和6年（2024年）分・12府県（青森・福島・栃木・埼玉・千葉・神奈川・京都・大阪・徳島・
佐賀・宮崎・鹿児島）を収録します。対象は利用規約で商用利用・再配布可を確認できた府県だけです。

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
値は空欄と同じく NULL に置き換えています。

## crime.prefecture_crime

警察庁の犯罪統計資料（1～12月分の確定値）の都道府県別表です。1年×1罪種×1都道府県で1行、
2020年から2025年までを収録します。全都道府県を警察庁の同じ定義で集計した値なので、
theft（12府県・町丁目単位）の件数を全国の中で位置づける基準に使えます。

- year: 対象年（INTEGER、西暦。1～12月の確定値）
- crime_type: 罪種（VARCHAR、刑法犯総数／窃盗犯総数／重要犯罪総数／殺人／強盗／侵入強盗／放火／
  強制性交等（2022年まで）／不同意性交等（2023年から）／略取誘拐・人身売買／強制わいせつ（2022年まで）／
  不同意わいせつ（2023年から）／重要窃盗犯総数／侵入盗／
  侵入盗（住宅対象）／侵入盗（その他）／自動車盗／ひったくり／すり／主な街頭犯罪総数／器物損壊／住居侵入）
- prefecture_code: 都道府県コード（VARCHAR、JIS X 0401 の2桁）
- prefecture: 都道府県（VARCHAR、北海道は方面別の内訳を畳んだ道全体の値）
- recognized_cases: 認知件数（INTEGER）
- cleared_cases: 検挙件数（INTEGER、前年以前に認知した事件の検挙を含む）
- arrested_persons: 検挙人員（INTEGER）

原表は第3表（刑法犯総数）・第4表（窃盗犯総数）・第6表（重要犯罪・重要窃盗犯）・第9表（街頭犯罪等）で、
当年と前年を並べた対前年比較の形なので当年の列だけを採っています。月次の暫定値は収録しません。
罪種は互いに包含関係がある（侵入強盗は強盗の内数、侵入盗は重要窃盗犯と窃盗犯の内数、窃盗犯は刑法犯の内数など）
ため、罪種をまたいで合計しないでください。2023年の刑法改正で強制性交等・強制わいせつは
不同意性交等・不同意わいせつに置き換わり構成要件も変わったため、公表どおり別の罪種名で持ちます。
主な街頭犯罪総数は路上強盗・部品ねらい・車上ねらい・自動販売機ねらい・オートバイ盗・自転車盗の合計です。
検挙率は cleared_cases ÷ recognized_cases で求められ、100%を超えることがあります。

## crime.special_fraud

警察庁の特殊詐欺の認知・検挙状況の手口別・月別表です。1区分×1か月×1手口で1行、2020年1月から
最新の公表月までを収録します。全国の値だけで、都道府県別の値はありません。

- classification_year: 手口の区分（INTEGER、区分の適用開始年。2020 は令和2年の10類型、2026 は令和8年の区分）
- year: 対象年（INTEGER、西暦）
- month: 対象月（INTEGER、1〜12）
- month_start: 対象月の初日（DATE）
- modus: 手口（VARCHAR、特殊詐欺（全手口の合計）／オレオレ詐欺／預貯金詐欺／架空料金請求詐欺／還付金詐欺／
  融資保証金詐欺／金融商品詐欺／ギャンブル詐欺／交際あっせん詐欺／キャッシュカード詐欺盗／その他の特殊詐欺。
  令和8年の区分ではニセ警察詐欺／SNS型投資詐欺／SNS型ロマンス詐欺が加わる）
- is_provisional: 暫定値か（BOOLEAN、当年の公表月までの値）
- recognized_cases: 認知件数（INTEGER）
- completed_cases: 既遂件数（INTEGER、認知件数のうち既遂）
- damage_amount_yen: 実質的な被害総額（BIGINT、円。ATM から引き出された額を加えた額。還付金詐欺は NULL）
- completed_damage_amount_yen: 被害総額・既遂のみ（BIGINT、円。還付金詐欺は両区分、その他の手口は令和2年の区分だけ）
- cleared_cases: 検挙件数（INTEGER、ニセ警察詐欺の2025年は NULL）
- arrested_persons: 検挙人員（INTEGER、ニセ警察詐欺の2025年は NULL）

2020〜2025年は年別の確定値ファイル（令和2年の区分）の当年の表を、最新の暫定値ファイル（令和8年の区分）
からは当年と前年の表を採っています。令和8年からニセ警察詐欺が独立し、SNS型投資詐欺・SNS型ロマンス詐欺が
特殊詐欺の手口に加わったため、2025年は両方の区分で収録されていて、令和8年の区分の方が特殊詐欺全体の
件数も被害額も大きくなります。区分をまたいで系列を連結・合計しないでください。
modus が「特殊詐欺」の行は全手口の合計なので、手口の行と足し合わせないでください。
形態（文言）別の内訳表と、組織的犯罪処罰法違反などの関連法令の表は収録しません。

## crime.tokyo_town_crime

警視庁の町丁字別・罪種別・手口別の認知件数（年累計）です。1年×1町丁字で1行、2009年から2025年まで、
1年あたり約5,000〜5,200町丁字を収録します。認知が0件の町丁字は行がありません。

- year: 対象年（INTEGER、西暦。1〜12月の年累計）
- city_code: 市区町村コード（VARCHAR、全国地方公共団体コード6桁）
- municipality: 区市町村（VARCHAR、原表の郡名・島名を外した名前）
- town: 町丁字（VARCHAR、区市町村名と全角空白を除いた原表の文字列。丁目の数字は全角。「以下不詳」は町丁字が不明の認知、
  NULL は区市町村名だけの行で、檜原村・神津島村・利島村・青ヶ島村・御蔵島村の5村にだけある）
- total: 総合計（INTEGER）
- heinous_total: 凶悪犯計（INTEGER）
- heinous_robbery: 凶悪犯強盗（INTEGER）
- heinous_other: 凶悪犯その他（INTEGER）
- violent_total: 粗暴犯計（INTEGER）
- violent_unlawful_assembly: 粗暴犯凶器準備集合（INTEGER）
- violent_assault: 粗暴犯暴行（INTEGER）
- violent_injury: 粗暴犯傷害（INTEGER）
- violent_intimidation: 粗暴犯脅迫（INTEGER）
- violent_extortion: 粗暴犯恐喝（INTEGER）
- burglary_total: 侵入窃盗計（INTEGER）
- burglary_safe: 侵入窃盗金庫破り（INTEGER）
- burglary_school: 侵入窃盗学校荒し（INTEGER）
- burglary_office: 侵入窃盗事務所荒し（INTEGER）
- burglary_shop: 侵入窃盗出店荒し（INTEGER）
- burglary_vacant_house: 侵入窃盗空き巣（INTEGER）
- burglary_night: 侵入窃盗忍込み（INTEGER）
- burglary_occupied_house: 侵入窃盗居空き（INTEGER）
- burglary_other: 侵入窃盗その他（INTEGER）
- non_burglary_total: 非侵入窃盗計（INTEGER）
- non_burglary_car: 非侵入窃盗自動車盗（INTEGER）
- non_burglary_motorcycle: 非侵入窃盗オートバイ盗（INTEGER）
- non_burglary_bicycle: 非侵入窃盗自転車盗（INTEGER）
- non_burglary_from_car: 非侵入窃盗車上ねらい（INTEGER）
- non_burglary_vending_machine: 非侵入窃盗自販機ねらい（INTEGER）
- non_burglary_construction_site: 非侵入窃盗工事場ねらい（INTEGER）
- non_burglary_pickpocket: 非侵入窃盗すり（INTEGER）
- non_burglary_snatching: 非侵入窃盗ひったくり（INTEGER）
- non_burglary_unattended: 非侵入窃盗置引き（INTEGER）
- non_burglary_shoplifting: 非侵入窃盗万引き（INTEGER）
- non_burglary_other: 非侵入窃盗その他（INTEGER）
- other_total: その他計（INTEGER）
- other_fraud: その他詐欺（INTEGER）
- other_embezzlement_lost_property: その他占有離脱物横領（INTEGER）
- other_intellectual: その他その他知能犯（INTEGER）
- other_gambling: その他賭博（INTEGER）
- other_penal_code: その他その他刑法犯（INTEGER）

総合計は罪種の計（凶悪犯計・粗暴犯計・侵入窃盗計・非侵入窃盗計・その他計）の合計、罪種の計はその手口の合計で、
取得時に全行で一致を確かめています。区市町村計と都全体の合計の行も、町丁字の行の合計と突き合わせたうえで
収録から外しています。発生地が都外（他県）・海外・不明の認知は町丁字に属さないので収録しません。
そのため町丁字を合計しても都全体の認知件数とは一致しません。当年の月累計（年途中の値）は収録しません。

## 更新

```bash
uv sync
bash scripts/build.sh
```
