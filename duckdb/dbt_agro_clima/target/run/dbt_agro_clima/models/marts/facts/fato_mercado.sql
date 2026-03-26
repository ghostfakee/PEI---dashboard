
  
    
    

    create  table
      "dev"."main"."fato_mercado__dbt_tmp"
  
    as (
      with mercado as (

    select * from "dev"."main"."int_mercado_enriquecido"

),

tempo as (

    select * from "dev"."main"."dim_tempo"

),

empresa as (

    select * from "dev"."main"."dim_empresa"

)

select
    t.id_tempo,
    e.id_empresa,
    m.preco_abertura,
    m.preco_maximo,
    m.preco_minimo,
    m.preco_fechamento,
    m.volume,
    m.retorno_diario,
    m.media_movel_7d
from mercado m
inner join tempo t
    on m.data = t.data
inner join empresa e
    on m.ticker = e.ticker
    );
  
  