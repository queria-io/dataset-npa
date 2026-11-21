{# 特殊詐欺の統計の生データをそのまま mart に渡す。 #}

select * from {{ ref('raw_fraud_stats') }}
