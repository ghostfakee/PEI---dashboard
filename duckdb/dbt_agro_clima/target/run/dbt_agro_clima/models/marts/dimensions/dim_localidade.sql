
  
    
    

    create  table
      "dev"."main"."dim_localidade__dbt_tmp"
  
    as (
      with localidades as (

    select distinct
        estado,
        cidade,
        latitude,
        longitude
    from "dev"."main"."int_clima_mercado"

)

select
    row_number() over (order by estado, cidade) as id_localidade,
    estado,
    cidade,
    latitude,
    longitude,
    'MT_agro' as regiao_agro
from localidades
    );
  
  