{# 原表の地域2列から都道府県を取り出し、JIS の都道府県コードを付ける。
   東京都は地方の列に単独で書かれ、北海道は「計」の行が道全体を表す。
   全国・地方計・北海道の方面別の行は prefecture が NULL になる。 #}

with prefectures as (
    select
        unnest([
            '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
            '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
            '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
            '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
            '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
            '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
        ]) as prefecture,
        unnest(range(1, 48)) as n
),

areas as (
    select
        *,
        case
            when area_group = '東京都' then '東京都'
            when area_group = '北海道' and area = '計' then '北海道'
            when area_group <> '北海道' and area <> '計' then area
        end as prefecture_name
    from {{ ref('raw_crime_stats') }}
)

select
    a.year,
    a.crime_type,
    a.area_group,
    a.area,
    lpad(p.n::varchar, 2, '0') as prefecture_code,
    p.prefecture,
    a.recognized_cases,
    a.cleared_cases,
    a.arrested_persons
from areas as a
left join prefectures as p on a.prefecture_name = p.prefecture
