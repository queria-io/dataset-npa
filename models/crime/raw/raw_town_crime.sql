{# 警視庁 区市町村の町丁別、罪種別及び手口別認知件数（年累計）の生データ。
   main.py が年別の Excel / CSV から町丁字の行だけを取り出し、.queria/npa_town_crime.csv に保存する。
   区市町村計・合計の行との突き合わせは取得時に済ませてある。 #}

{{ config(materialized='table') }}

select *
from read_csv(
    '.queria/npa_town_crime.csv',
    header=true,
    columns={
        'year': 'INTEGER',
        'city_code': 'VARCHAR',
        'municipality': 'VARCHAR',
        'town': 'VARCHAR',
        'total': 'INTEGER',
        'heinous_total': 'INTEGER',
        'heinous_robbery': 'INTEGER',
        'heinous_other': 'INTEGER',
        'violent_total': 'INTEGER',
        'violent_unlawful_assembly': 'INTEGER',
        'violent_assault': 'INTEGER',
        'violent_injury': 'INTEGER',
        'violent_intimidation': 'INTEGER',
        'violent_extortion': 'INTEGER',
        'burglary_total': 'INTEGER',
        'burglary_safe': 'INTEGER',
        'burglary_school': 'INTEGER',
        'burglary_office': 'INTEGER',
        'burglary_shop': 'INTEGER',
        'burglary_vacant_house': 'INTEGER',
        'burglary_night': 'INTEGER',
        'burglary_occupied_house': 'INTEGER',
        'burglary_other': 'INTEGER',
        'non_burglary_total': 'INTEGER',
        'non_burglary_car': 'INTEGER',
        'non_burglary_motorcycle': 'INTEGER',
        'non_burglary_bicycle': 'INTEGER',
        'non_burglary_from_car': 'INTEGER',
        'non_burglary_vending_machine': 'INTEGER',
        'non_burglary_construction_site': 'INTEGER',
        'non_burglary_pickpocket': 'INTEGER',
        'non_burglary_snatching': 'INTEGER',
        'non_burglary_unattended': 'INTEGER',
        'non_burglary_shoplifting': 'INTEGER',
        'non_burglary_other': 'INTEGER',
        'other_total': 'INTEGER',
        'other_fraud': 'INTEGER',
        'other_embezzlement_lost_property': 'INTEGER',
        'other_intellectual': 'INTEGER',
        'other_gambling': 'INTEGER',
        'other_penal_code': 'INTEGER'
    }
)
