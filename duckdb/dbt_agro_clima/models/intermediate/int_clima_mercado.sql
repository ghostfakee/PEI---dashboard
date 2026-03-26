with clima as (

    select * from {{ ref('int_clima_enriquecido') }}

),

mercado as (

    select * from {{ ref('int_mercado_enriquecido') }}

),

final as (

    select
        c.data,
        c.estado,
        c.cidade,
        c.latitude,
        c.longitude,
        m.ticker,

        c.temperatura_media,
        c.temperatura_maxima,
        c.temperatura_minima,
        c.precipitacao_mm,
        c.velocidade_vento,
        c.chuva_acumulada_7d,
        c.temperatura_media_7d,
        c.precipitacao_lag_7d,

        m.preco_abertura,
        m.preco_maximo,
        m.preco_minimo,
        m.preco_fechamento,
        m.volume,
        m.retorno_diario,
        m.media_movel_7d

    from clima c
    inner join mercado m
        on c.data = m.data

)

select * from final