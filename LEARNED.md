## Phase1

> **"In the Bronze layer, data should be stored exactly as received from the source — no transformation, no field selection. I initially extracted only `properties` and dropped `geometry`, which meant I'd already lost part of the raw data. I also tried saving as Parquet, but Parquet is a columnar format — it requires a predefined, flat schema, so you can't store arbitrary nested JSON as-is. JSON, being flexible and schema-less, is the right format for Bronze. Parquet makes more sense later, in Silver/Gold, once the data has a defined structure."**
