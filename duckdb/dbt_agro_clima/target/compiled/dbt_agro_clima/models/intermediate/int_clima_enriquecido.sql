with base as (

    select * from "dev"."main"."stg_clima"

),

final as (

    select
        data,
        estado,
        cidade,
        latitude,
        longitude,
        temperatura_media,
        temperatura_maxima,
        temperatura_minima,
        precipitacao_mm,
        velocidade_vento,

        sum(precipitacao_mm) over (
            partition by estado, cidade
            order by data
            rows between 6 preceding and current row
        ) as chuva_acumulada_7d,

        avg(temperatura_media) over (
            partition by estado, cidade
            order by data
            rows between 6 preceding and current row
        ) as temperatura_media_7d,

        lag(precipitacao_mm, 7) over (
            partition by estado, cidade
            order by data
        ) as precipitacao_lag_7d

    from base

)

select * from final