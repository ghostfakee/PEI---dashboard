with source as (

    select *
    from read_parquet('C:/Users/lucas.barros/Documents/duckdb/data/raw/clima/**/*.parquet')

),

renamed as (

    select
        cast(data as date) as data,
        upper(trim(estado)) as estado,
        trim(cidade) as cidade,
        cast(latitude as double) as latitude,
        cast(longitude as double) as longitude,
        cast(temperatura_media as double) as temperatura_media,
        cast(temperatura_maxima as double) as temperatura_maxima,
        cast(temperatura_minima as double) as temperatura_minima,
        cast(precipitacao_mm as double) as precipitacao_mm,
        cast(velocidade_vento as double) as velocidade_vento
    from source

),

deduplicated as (

    select distinct *
    from renamed

)

select * from deduplicated