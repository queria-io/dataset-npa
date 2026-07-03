{# 警察庁 交通事故統計（本票）の生データ。
   main.py が年別本票 CSV を取得・正規化して .fdl/npa_honhyo.csv に保存する。
   コード列は先頭ゼロを保持するため VARCHAR で読む。 #}

{{ config(materialized='table') }}

select *
from read_csv(
    '.fdl/npa_honhyo.csv',
    header=true,
    columns={
        'prefecture_code': 'VARCHAR',
        'police_station_code': 'VARCHAR',
        'accident_number': 'VARCHAR',
        'accident_type_code': 'VARCHAR',
        'fatalities': 'INTEGER',
        'injuries': 'INTEGER',
        'city_code': 'VARCHAR',
        'occurred_year': 'INTEGER',
        'occurred_month': 'INTEGER',
        'occurred_day': 'INTEGER',
        'occurred_hour': 'INTEGER',
        'occurred_minute': 'INTEGER',
        'day_night_code': 'VARCHAR',
        'weather_code': 'VARCHAR',
        'terrain_code': 'VARCHAR',
        'road_surface_code': 'VARCHAR',
        'road_shape_code': 'VARCHAR',
        'traffic_signal_code': 'VARCHAR',
        'accident_pattern_code': 'VARCHAR',
        'day_of_week_code': 'VARCHAR',
        'holiday_code': 'VARCHAR',
        'latitude_dms': 'VARCHAR',
        'longitude_dms': 'VARCHAR'
    }
)
