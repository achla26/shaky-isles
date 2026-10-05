SELECT time::date as quake_date , COUNT(*) as quake_count FROM {{ref('stg_quakes')}}
GROUP BY time::date