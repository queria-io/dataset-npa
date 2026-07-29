{# 都道府県警察 犯罪発生情報の生データ。
   main.py が県警別・手口別の年別 CSV を取得・統合して .queria/npa_crime.csv に保存する。
   日付・時刻は「不明」等の非数値表現を含むため VARCHAR のまま読む。 #}

{{ config(materialized='table') }}

select *
from read_csv(
    '.queria/npa_crime.csv',
    header=true,
    columns={
        'crime_name': 'VARCHAR',
        'modus': 'VARCHAR',
        'police_station': 'VARCHAR',
        'police_box': 'VARCHAR',
        'city_code': 'VARCHAR',
        'prefecture': 'VARCHAR',
        'city': 'VARCHAR',
        'town': 'VARCHAR',
        'occurred_date_raw': 'VARCHAR',
        'occurred_hour_raw': 'VARCHAR',
        'location': 'VARCHAR',
        'location_detail': 'VARCHAR',
        'victim_gender': 'VARCHAR',
        'victim_age': 'VARCHAR',
        'victim_occupation': 'VARCHAR',
        'cash_damage': 'VARCHAR',
        'lock_status': 'VARCHAR',
        'anti_theft_device': 'VARCHAR',
        'stolen_property': 'VARCHAR',
        'source_prefecture': 'VARCHAR',
        'data_year': 'INTEGER'
    }
)
