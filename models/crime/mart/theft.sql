{# 犯罪発生情報（窃盗の街頭犯罪）。1認知件1レコード・町丁目単位。 #}

{{ config(materialized='table') }}

select
    crime_name,
    modus,
    prefecture,
    city_code,
    city,
    town,
    occurred_date,
    occurred_hour,
    location,
    location_detail,
    police_station,
    police_box,
    victim_gender,
    victim_age,
    victim_occupation,
    cash_damage,
    lock_status,
    anti_theft_device,
    stolen_property,
    source_prefecture,
    data_year
from {{ ref('stg_theft') }}
