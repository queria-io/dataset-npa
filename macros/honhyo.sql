{#
  本票（交通事故）のコード値を名称に変換するマクロ群。
  コード定義は警察庁「各種コード表」（codebook）に準拠する。
#}

{% macro prefecture_name(col) %}
  CASE {{ col }}
    WHEN '10' THEN '北海道（札幌方面）'
    WHEN '11' THEN '北海道（函館方面）'
    WHEN '12' THEN '北海道（旭川方面）'
    WHEN '13' THEN '北海道（釧路方面）'
    WHEN '14' THEN '北海道（北見方面）'
    WHEN '20' THEN '青森'
    WHEN '21' THEN '岩手'
    WHEN '22' THEN '宮城'
    WHEN '23' THEN '秋田'
    WHEN '24' THEN '山形'
    WHEN '25' THEN '福島'
    WHEN '30' THEN '東京'
    WHEN '40' THEN '茨城'
    WHEN '41' THEN '栃木'
    WHEN '42' THEN '群馬'
    WHEN '43' THEN '埼玉'
    WHEN '44' THEN '千葉'
    WHEN '45' THEN '神奈川'
    WHEN '46' THEN '新潟'
    WHEN '47' THEN '山梨'
    WHEN '48' THEN '長野'
    WHEN '49' THEN '静岡'
    WHEN '50' THEN '富山'
    WHEN '51' THEN '石川'
    WHEN '52' THEN '福井'
    WHEN '53' THEN '岐阜'
    WHEN '54' THEN '愛知'
    WHEN '55' THEN '三重'
    WHEN '60' THEN '滋賀'
    WHEN '61' THEN '京都'
    WHEN '62' THEN '大阪'
    WHEN '63' THEN '兵庫'
    WHEN '64' THEN '奈良'
    WHEN '65' THEN '和歌山'
    WHEN '70' THEN '鳥取'
    WHEN '71' THEN '島根'
    WHEN '72' THEN '岡山'
    WHEN '73' THEN '広島'
    WHEN '74' THEN '山口'
    WHEN '80' THEN '徳島'
    WHEN '81' THEN '香川'
    WHEN '82' THEN '愛媛'
    WHEN '83' THEN '高知'
    WHEN '90' THEN '福岡'
    WHEN '91' THEN '佐賀'
    WHEN '92' THEN '長崎'
    WHEN '93' THEN '熊本'
    WHEN '94' THEN '大分'
    WHEN '95' THEN '宮崎'
    WHEN '96' THEN '鹿児島'
    WHEN '97' THEN '沖縄'
  END
{% endmacro %}

{% macro accident_type_name(col) %}
  CASE {{ col }}
    WHEN '1' THEN '死亡'
    WHEN '2' THEN '負傷'
  END
{% endmacro %}

{% macro day_night_name(col) %}
  CASE {{ col }}
    WHEN '11' THEN '昼－明'
    WHEN '12' THEN '昼－昼'
    WHEN '13' THEN '昼－暮'
    WHEN '21' THEN '夜－暮'
    WHEN '22' THEN '夜－夜'
    WHEN '23' THEN '夜－明'
  END
{% endmacro %}

{% macro weather_name(col) %}
  CASE {{ col }}
    WHEN '1' THEN '晴'
    WHEN '2' THEN '曇'
    WHEN '3' THEN '雨'
    WHEN '4' THEN '霧'
    WHEN '5' THEN '雪'
  END
{% endmacro %}

{% macro terrain_name(col) %}
  CASE {{ col }}
    WHEN '1' THEN '市街地－人口集中'
    WHEN '2' THEN '市街地－その他'
    WHEN '3' THEN '非市街地'
  END
{% endmacro %}

{% macro road_surface_name(col) %}
  CASE {{ col }}
    WHEN '1' THEN '舗装－乾燥'
    WHEN '2' THEN '舗装－湿潤'
    WHEN '3' THEN '舗装－凍結'
    WHEN '4' THEN '舗装－積雪'
    WHEN '5' THEN '非舗装'
  END
{% endmacro %}

{% macro road_shape_name(col) %}
  CASE {{ col }}
    WHEN '31' THEN '交差点－環状交差点'
    WHEN '01' THEN '交差点－その他'
    WHEN '37' THEN '交差点付近－環状交差点付近'
    WHEN '07' THEN '交差点付近－その他'
    WHEN '11' THEN '単路－トンネル'
    WHEN '12' THEN '単路－橋'
    WHEN '13' THEN '単路－カーブ・屈折'
    WHEN '14' THEN '単路－その他'
    WHEN '21' THEN '踏切－第一種'
    WHEN '22' THEN '踏切－第三種'
    WHEN '23' THEN '踏切－第四種'
    WHEN '00' THEN '一般交通の場所'
  END
{% endmacro %}

{% macro traffic_signal_name(col) %}
  CASE {{ col }}
    WHEN '1' THEN '点灯－３灯式'
    WHEN '8' THEN '点灯－歩車分式'
    WHEN '2' THEN '点灯－押ボタン式'
    WHEN '3' THEN '点滅－３灯式'
    WHEN '4' THEN '点滅－１灯式'
    WHEN '5' THEN '消灯'
    WHEN '6' THEN '故障'
    WHEN '7' THEN '施設なし'
  END
{% endmacro %}

{% macro accident_pattern_name(col) %}
  CASE {{ col }}
    WHEN '01' THEN '人対車両'
    WHEN '21' THEN '車両相互'
    WHEN '41' THEN '車両単独'
    WHEN '61' THEN '列車'
  END
{% endmacro %}

{% macro day_of_week_name(col) %}
  CASE {{ col }}
    WHEN '1' THEN '日'
    WHEN '2' THEN '月'
    WHEN '3' THEN '火'
    WHEN '4' THEN '水'
    WHEN '5' THEN '木'
    WHEN '6' THEN '金'
    WHEN '7' THEN '土'
  END
{% endmacro %}

{% macro holiday_name(col) %}
  CASE {{ col }}
    WHEN '1' THEN '当日'
    WHEN '2' THEN '前日'
    WHEN '3' THEN 'その他'
  END
{% endmacro %}

{#
  緯度・経度は度分秒を桁で連結した固定長文字列。
    - 緯度（9桁）: DDMMSSsss = 度(2) 分(2) 秒(2) 秒の小数3桁
    - 経度（10桁）: DDDMMSSsss = 度(3) 分(2) 秒(2) 秒の小数3桁
  これを十進度へ変換する。
#}
{% macro dms_to_decimal(col, deg_digits) %}
  (
    CAST(substr({{ col }}, 1, {{ deg_digits }}) AS INTEGER)
    + CAST(substr({{ col }}, {{ deg_digits + 1 }}, 2) AS INTEGER) / 60.0
    + (CAST(substr({{ col }}, {{ deg_digits + 3 }}, 5) AS INTEGER) / 1000.0) / 3600.0
  )
{% endmacro %}
