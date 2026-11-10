{# 交通事故統計の都道府県コード（警察の管轄区分）と JIS X 0401 の都道府県コードの対応表。
   値は police_prefectures() マクロの 1 か所から作り、traffic_accident の変換と同じものを公開する。 #}

{{ config(materialized='table') }}

select * from (values
{%- for code, p in police_prefectures().items() %}
    ('{{ code }}', '{{ p.name }}', '{{ p.jis }}'){{ "," if not loop.last }}
{%- endfor %}
) as t(prefecture_code, prefecture, jis_prefecture_code)
order by prefecture_code
