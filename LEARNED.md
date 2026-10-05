> **Phase 1 fetch raw data**
>
> "In the Bronze layer, data should be stored exactly as received from the source — no transformation, no field selection. I initially extracted only `properties` and dropped `geometry`, which meant I'd already lost part of the raw data. I also tried saving as Parquet, but Parquet is a columnar format — it requires a predefined, flat schema, so you can't store arbitrary nested JSON as-is. JSON, being flexible and schema-less, is the right format for Bronze. Parquet makes more sense later, in Silver/Gold, once the data has a defined structure."

 

> **Phase 2 — Load (Bronze → DuckDB)**
>
> In this phase, I learned how to load raw JSON data into a database table while keeping it idempotent. Each row stores the full raw record as a JSON string (`raw_json`), along with an `ingested_at` timestamp to track when the data was loaded — useful for auditing and as a foundation for watermark-based incremental loads later.
>
> To achieve idempotency, I used the quake's unique identifier (`publicID`) as a dedup key: before inserting, I check which IDs already exist in the table and only insert rows with new IDs (`WHERE quake_id NOT IN (...)`). This means running the same load script multiple times never creates duplicate records — a core requirement for reliable, repeatable pipelines.


> **Phase 3 — Transform (dbt)**
>
> In this phase, I connected dbt to my DuckDB database by configuring credentials in `profiles.yml`. I registered the existing raw table as a dbt source using `sources.yml`, which tells dbt where the raw data lives (schema + table name).
>
> I then built a staging model (`stg_quakes`) that parses the raw JSON column into proper typed columns, using DuckDB's `json_extract_string()` function to pull values out of the JSON by path (e.g., `$.properties.magnitude`) and casting them to the right types (double, integer, timestamp).
>
> On top of staging, I built a mart model (`mart_daily_counts`) that aggregates quakes by day using `GROUP BY`. Since dbt's default materialization is a **view**, these models don't store data physically — they're saved queries that run live against the source each time. Tables would be needed for faster, persisted results.
>
> Finally, I added tests in `schema.yml` — `not_null` and `unique` — on key columns in both models, and confirmed all 5 tests passed with `dbt test`.
 