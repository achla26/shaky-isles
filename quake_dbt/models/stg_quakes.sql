with extracted as (
    select
        quake_id,
        json_extract_string(raw_json, '$.properties.time')::timestamp as time,
        json_extract_string(raw_json, '$.properties.depth')::double as depth,
        json_extract_string(raw_json, '$.properties.magnitude')::double as magnitude,
        json_extract_string(raw_json, '$.properties.mmi')::integer as mmi,
        json_extract_string(raw_json, '$.properties.locality') as locality,
        json_extract_string(raw_json, '$.properties.quality') as quality,
        json_extract_string(raw_json, '$.geometry.coordinates[0]')::double as longitude,
        json_extract_string(raw_json, '$.geometry.coordinates[1]')::double as latitude,
        ingested_at
    from {{ source('raw', 'quakes') }}
)

select *
from extracted
where magnitude is not null