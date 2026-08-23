{# 発生年月日・発生時を型変換し、市区町村コードの先頭ゼロ欠落を復元する。
   「不明」・空欄は NULL とする（発生地不明のレコードも原典どおり保持する）。 #}

select
    crime_name,
    modus,
    police_station,
    police_box,
    -- 栃木県は Excel 由来の先頭ゼロ欠落で5桁になっているため6桁へ復元する
    case
        when length(city_code) = 6 then city_code
        when length(city_code) = 5 then '0' || city_code
    end as city_code,
    -- 発生地不明を空欄ではなく「日本国内のいずれかの場所」等の文言で表す県があるため、
    -- 都道府県名でない値は空欄と同じく NULL に寄せる
    case
        when regexp_matches(prefecture, '(都|道|府|県)$') then prefecture
    end as prefecture,
    city,
    town,
    -- YYYYMMDD 形式のみ日付化。「不明」等は NULL
    case
        when regexp_matches(occurred_date_raw, '^\d{8}$')
        then try_strptime(occurred_date_raw, '%Y%m%d')::date
    end as occurred_date,
    case
        when try_cast(occurred_hour_raw as integer) between 0 and 23
        then try_cast(occurred_hour_raw as integer)
    end as occurred_hour,
    location,
    location_detail,
    victim_gender,
    victim_age,
    victim_occupation,
    cash_damage,
    lock_status,
    anti_theft_device,
    stolen_property,
    source_prefecture,
    data_year
from {{ ref('raw_theft') }}
