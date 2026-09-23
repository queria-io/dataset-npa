{# 犯罪統計（確定値）の都道府県別・罪種別の認知件数・検挙件数・検挙人員。1年×1罪種×1都道府県で1行。 #}

{{ config(materialized='table') }}

select
    year,
    crime_type,
    prefecture_code,
    prefecture,
    recognized_cases,
    cleared_cases,
    arrested_persons
from {{ ref('stg_crime_stats') }}
where prefecture is not null
