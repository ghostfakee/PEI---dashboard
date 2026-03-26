with clima as (

    select * from "dev"."main"."int_clima_enriquecido"

),

tempo as (

    select * from "dev"."main"."dim_tempo"

),

localidade as (

    select * from "dev"."main"."dim_localidade"

)

select
    t.id_tempo,
    l.id_localidade,
    c.temperatura_media,
    c.temperatura_maxima,
    c.temperatura_minima,
    c.precipitacao_mm,
    c.velocidade_vento,
    c.chuva_acumulada_7d,
    c.temperatura_media_7d,
    c.precipitacao_lag_7d
from clima c
inner join tempo t
    on c.data = t.data
inner join localidade l
    on c.estado = l.estado
   and c.cidade = l.cidade