{# 交通事故統計の都道府県コード（警察の管轄区分）と JIS X 0401 の都道府県コードの対応表。
   seeds/police_prefecture.csv をそのまま公開する。traffic_accident もこの表と結合して変換する。 #}

{{ config(materialized='table') }}

select prefecture_code, prefecture, jis_prefecture_code
from {{ ref('police_prefecture') }}
order by prefecture_code
