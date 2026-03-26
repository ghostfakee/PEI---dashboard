with base as (

    select * from "dev"."main"."stg_mercado"

),

final as (

    select
        data,
        ticker,
        preco_abertura,
        preco_maximo,
        preco_minimo,
        preco_fechamento,
        volume,

        (
            preco_fechamento
            - lag(preco_fechamento) over (
                partition by ticker
                order by data
            )
        )
        / nullif(
            lag(preco_fechamento) over (
                partition by ticker
                order by data
            ),
            0
        ) as retorno_diario,

        avg(preco_fechamento) over (
            partition by ticker
            order by data
            rows between 6 preceding and current row
        ) as media_movel_7d

    from base

)

select * from final