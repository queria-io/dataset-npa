{#
  本票（交通事故）のコード値を名称に変換するマクロ群。
  コード定義は警察庁「各種コード表」（codebook）に準拠する。
#}

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
