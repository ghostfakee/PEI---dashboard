with source as (

    select *
    from read_parquet('C:/Users/lucas.barros/Documents/duckdb/data/raw/bolsa/**/*.parquet')

),

renamed as (

    select
        cast(data as date) as data,
        upper(trim(ticker)) as ticker,
        cast(preco_abertura as double) as preco_abertura,
        cast(preco_maximo as double) as preco_maximo,
        cast(preco_minimo as double) as preco_minimo,
        cast(preco_fechamento as double) as preco_fechamento,
        cast(volume as bigint) as volume
    from source

),

deduplicated as (

    select distinct *
    from renamed

)

select * from deduplicated