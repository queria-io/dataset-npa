{# 特殊詐欺の全国の手口別・月別の認知件数・被害額・検挙件数・検挙人員。1区分×1か月×1手口で1行。 #}

{{ config(materialized='table') }}

select
    classification_year,
    year,
    month,
    make_date(year, month, 1) as month_start,
    modus,
    is_provisional,
    recognized_cases,
    completed_cases,
    damage_amount_yen,
    completed_damage_amount_yen,
    cleared_cases,
    arrested_persons
from {{ ref('raw_fraud_stats') }}
