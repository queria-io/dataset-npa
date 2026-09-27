{# 警察庁「特殊詐欺の認知・検挙状況等について」の手口別・月別表の生データ。
   main.py が年別の確定値と最新の暫定値の Excel から、.queria/npa_fraud_stats.csv に手口×年月で保存する。
   同じ年が令和2年と令和8年の2つの区分で重なることがあるので、classification_year で区別する。 #}

{{ config(materialized='table') }}

select *
from read_csv(
    '.queria/npa_fraud_stats.csv',
    header=true,
    columns={
        'classification_year': 'INTEGER',
        'year': 'INTEGER',
        'month': 'INTEGER',
        'modus': 'VARCHAR',
        'is_provisional': 'BOOLEAN',
        'recognized_cases': 'INTEGER',
        'completed_cases': 'INTEGER',
        'damage_amount_yen': 'BIGINT',
        'completed_damage_amount_yen': 'BIGINT',
        'cleared_cases': 'INTEGER',
        'arrested_persons': 'INTEGER'
    }
)
