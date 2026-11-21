{# 警視庁の町丁字別認知件数の生データをそのまま mart に渡す。 #}

select * from {{ ref('raw_town_crime') }}
