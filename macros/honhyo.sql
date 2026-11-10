{#
  本票（交通事故）のコード値を名称に変換するマクロ群。
  コード定義は警察庁「各種コード表」（codebook）に準拠する。
#}

{# 警察の都道府県コードごとの名称と JIS X 0401 の都道府県コード（2 桁）。
   JIS コードは「各種コード表」の都道府県名と JIS X 0401 の名前で決めている。
   北海道の 5 方面（10〜14）はどれも 01。 #}

{% macro police_prefectures() %}
  {% do return({
    '10': {'name': '北海道（札幌方面）', 'jis': '01'},
    '11': {'name': '北海道（函館方面）', 'jis': '01'},
    '12': {'name': '北海道（旭川方面）', 'jis': '01'},
    '13': {'name': '北海道（釧路方面）', 'jis': '01'},
    '14': {'name': '北海道（北見方面）', 'jis': '01'},
    '20': {'name': '青森', 'jis': '02'},
    '21': {'name': '岩手', 'jis': '03'},
    '22': {'name': '宮城', 'jis': '04'},
    '23': {'name': '秋田', 'jis': '05'},
    '24': {'name': '山形', 'jis': '06'},
    '25': {'name': '福島', 'jis': '07'},
    '30': {'name': '東京', 'jis': '13'},
    '40': {'name': '茨城', 'jis': '08'},
    '41': {'name': '栃木', 'jis': '09'},
    '42': {'name': '群馬', 'jis': '10'},
    '43': {'name': '埼玉', 'jis': '11'},
    '44': {'name': '千葉', 'jis': '12'},
    '45': {'name': '神奈川', 'jis': '14'},
    '46': {'name': '新潟', 'jis': '15'},
    '47': {'name': '山梨', 'jis': '19'},
    '48': {'name': '長野', 'jis': '20'},
    '49': {'name': '静岡', 'jis': '22'},
    '50': {'name': '富山', 'jis': '16'},
    '51': {'name': '石川', 'jis': '17'},
    '52': {'name': '福井', 'jis': '18'},
    '53': {'name': '岐阜', 'jis': '21'},
    '54': {'name': '愛知', 'jis': '23'},
    '55': {'name': '三重', 'jis': '24'},
    '60': {'name': '滋賀', 'jis': '25'},
    '61': {'name': '京都', 'jis': '26'},
    '62': {'name': '大阪', 'jis': '27'},
    '63': {'name': '兵庫', 'jis': '28'},
    '64': {'name': '奈良', 'jis': '29'},
    '65': {'name': '和歌山', 'jis': '30'},
    '70': {'name': '鳥取', 'jis': '31'},
    '71': {'name': '島根', 'jis': '32'},
    '72': {'name': '岡山', 'jis': '33'},
    '73': {'name': '広島', 'jis': '34'},
    '74': {'name': '山口', 'jis': '35'},
    '80': {'name': '徳島', 'jis': '36'},
    '81': {'name': '香川', 'jis': '37'},
    '82': {'name': '愛媛', 'jis': '38'},
    '83': {'name': '高知', 'jis': '39'},
    '90': {'name': '福岡', 'jis': '40'},
    '91': {'name': '佐賀', 'jis': '41'},
    '92': {'name': '長崎', 'jis': '42'},
    '93': {'name': '熊本', 'jis': '43'},
    '94': {'name': '大分', 'jis': '44'},
    '95': {'name': '宮崎', 'jis': '45'},
    '96': {'name': '鹿児島', 'jis': '46'},
    '97': {'name': '沖縄', 'jis': '47'},
  }) %}
{% endmacro %}

{% macro prefecture_name(col) %}
  CASE {{ col }}
  {%- for code, p in police_prefectures().items() %}
    WHEN '{{ code }}' THEN '{{ p.name }}'
  {%- endfor %}
  END
{% endmacro %}

{# 警察の都道府県コードを JIS X 0401 の都道府県コード（2 桁）に変換する。 #}

{% macro jis_prefecture_code(col) %}
  CASE {{ col }}
  {%- for code, p in police_prefectures().items() %}
    WHEN '{{ code }}' THEN '{{ p.jis }}'
  {%- endfor %}
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
