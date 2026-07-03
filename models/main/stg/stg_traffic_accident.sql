{# 緯度経度を十進度へ変換し、発生日時のタイムスタンプと事故識別子を付与する。
   時分が不正値（不明を表す 99 等）の行は occurred_at を NULL とし発生日は保持する。 #}

select
    occurred_year
        || '-' || prefecture_code
        || '-' || police_station_code
        || '-' || accident_number as accident_id,
    prefecture_code,
    police_station_code,
    accident_number,
    accident_type_code,
    fatalities,
    injuries,
    city_code,
    occurred_year,
    occurred_month,
    occurred_day,
    occurred_hour,
    occurred_minute,
    make_date(occurred_year, occurred_month, occurred_day) as occurred_date,
    case
        when occurred_hour between 0 and 23 and occurred_minute between 0 and 59
        then make_timestamp(
            occurred_year, occurred_month, occurred_day,
            occurred_hour, occurred_minute, 0
        )
    end as occurred_at,
    day_night_code,
    weather_code,
    terrain_code,
    road_surface_code,
    road_shape_code,
    traffic_signal_code,
    accident_pattern_code,
    day_of_week_code,
    holiday_code,
    {{ dms_to_decimal('latitude_dms', 2) }} as latitude,
    {{ dms_to_decimal('longitude_dms', 3) }} as longitude
from {{ ref('raw_traffic_accident') }}
