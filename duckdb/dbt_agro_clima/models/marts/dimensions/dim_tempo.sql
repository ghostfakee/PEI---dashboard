with datas as (

    select distinct data
    from {{ ref('int_clima_mercado') }}

)

select
    row_number() over (order by data) as id_tempo,
    data,
    year(data) as ano,
    case
        when month(data) between 1 and 6 then 1
        else 2
    end as semestre,
    month(data) as mes,
    day(data) as dia,
    dayofweek(data) as dia_semana
from datas