with empresas as (

    select distinct ticker
    from {{ ref('int_clima_mercado') }}

)

select
    row_number() over (order by ticker) as id_empresa,
    ticker,
    case
        when ticker = 'SLCE3' then 'SLC Agricola'
        else ticker
    end as nome_empresa,
    'Agro' as setor,
    'Agricultura' as subsetor
from empresas