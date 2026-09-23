{# 警察庁 犯罪統計資料（確定値）の都道府県別表の生データ。
   main.py が各年の Excel から当年の列を取り出し、.queria/npa_crime_stats.csv に縦持ちで保存する。
   地域は原表の2列（地方・都道府県）のままで、全国・地方計・北海道の方面別の行を含む。 #}

{{ config(materialized='table') }}

select *
from read_csv(
    '.queria/npa_crime_stats.csv',
    header=true,
    columns={
        'year': 'INTEGER',
        'crime_type': 'VARCHAR',
        'area_group': 'VARCHAR',
        'area': 'VARCHAR',
        'recognized_cases': 'INTEGER',
        'cleared_cases': 'INTEGER',
        'arrested_persons': 'INTEGER'
    }
)
