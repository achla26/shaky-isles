> **Phase 1 fetch raw data**
>
> "In the Bronze layer, data should be stored exactly as received from the source — no transformation, no field selection. I initially extracted only `properties` and dropped `geometry`, which meant I'd already lost part of the raw data. I also tried saving as Parquet, but Parquet is a columnar format — it requires a predefined, flat schema, so you can't store arbitrary nested JSON as-is. JSON, being flexible and schema-less, is the right format for Bronze. Parquet makes more sense later, in Silver/Gold, once the data has a defined structure."

 

> **Phase 2 — Load (Bronze → DuckDB)**
>
> In this phase, I learned how to load raw JSON data into a database table while keeping it idempotent. Each row stores the full raw record as a JSON string (`raw_json`), along with an `ingested_at` timestamp to track when the data was loaded — useful for auditing and as a foundation for watermark-based incremental loads later.
>
> To achieve idempotency, I used the quake's unique identifier (`publicID`) as a dedup key: before inserting, I check which IDs already exist in the table and only insert rows with new IDs (`WHERE quake_id NOT IN (...)`). This means running the same load script multiple times never creates duplicate records — a core requirement for reliable, repeatable pipelines.
 