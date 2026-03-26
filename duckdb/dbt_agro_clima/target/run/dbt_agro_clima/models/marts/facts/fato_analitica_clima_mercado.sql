
  
    
    

    create  table
      "dev"."main"."fato_analitica_clima_mercado__dbt_tmp"
  
    as (
      with base as (

    select * from "dev"."main"."int_clima_mercado"

),

tempo as (

    select * from "dev"."main"."dim_tempo"

),

localidade as (

    select * from "dev"."main"."dim_localidade"

),

empresa as (

    select * from "dev"."main"."dim_empresa"

)

select
    t.id_tempo,
    l.id_localidade,
    e.id_empresa,

    b.temperatura_media,
    b.temperatura_maxima,
    b.temperatura_minima,
    b.precipitacao_mm,
    b.velocidade_vento,
    b.chuva_acumulada_7d,
    b.temperatura_media_7d,
    b.precipitacao_lag_7d,

    b.preco_abertura,
    b.preco_maximo,
    b.preco_minimo,
    b.preco_fechamento,
    b.volume,
    b.retorno_diario,
    b.media_movel_7d

from base b
inner join tempo t
    on b.data = t.data
inner join localidade l
    on b.estado = l.estado
   and b.cidade = l.cidade
inner join empresa e
    on b.ticker = e.ticker
    );
  
  