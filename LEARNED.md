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
 

> **Phase 4A — Automate (GitHub Actions)**
>
> In this phase, I automated my pipeline to run on a schedule using GitHub Actions. A workflow file (`.github/workflows/quake.yml`) defines three things: **triggers** (`on:` — a cron schedule for hourly runs, plus `workflow_dispatch` for manual runs from the GitHub UI), a **job** (`runs-on: ubuntu-latest` — a fresh virtual machine), and **steps** (checkout code → set up Python → install dependencies → run my fetch, load, and dbt scripts in order).
>
> The key realization: each run happens on a **brand-new machine** that has no knowledge of my laptop — nothing exists there except what's committed to the Git repo. This meant my local `profiles.yml` (which lives outside the repo, in my home folder) wasn't available to dbt on the runner. I fixed this by adding a step that recreates the file at runtime (`mkdir -p ~/.dbt` + writing the file content via a heredoc) before running dbt.
>
> This also taught me an important security principle: hardcoding credentials into a workflow file is fine only when there's nothing sensitive to leak (like my local DuckDB file path). For a real cloud database with usernames/passwords, those values should never be committed to Git — instead, **GitHub Secrets** should be used to inject them securely as environment variables at runtime, since Git history is permanent and secrets committed once can't truly be "removed."
>
> Proof: workflow ran successfully end-to-end (green tick) on an hourly schedule, fully automated.

> **Phase 4B — Automate (Airflow, raw Docker Compose)**
>
> I set up a local Airflow environment using the official Apache Airflow `docker-compose.yaml` (switched from Astro after hitting a tool-specific volume-mount limitation — a good reminder that sometimes simpler, lower-level tools give more control than convenience wrappers).
>
> I wrote a TaskFlow DAG (`quake_elt`) with three tasks — `extract`, `load`, `transform` — chained with `>>`, scheduled `@hourly` with `catchup=False` to avoid backfilling old runs. I set `retries=2` on extract/load (network issues are often transient) but `retries=0` on transform (a failing dbt run usually means a real bug — retrying won't fix it).
>
> Debugging this taught me two important lessons:
> 1. **Missing dependencies:** the official Airflow image doesn't include libraries like `duckdb` by default — fixed using `_PIP_ADDITIONAL_REQUIREMENTS` in `.env` (a local-dev-only shortcut; production would bake dependencies into a custom image).
> 2. **Working directory consistency matters:** when multiple subprocess calls reference relative paths, they all need a consistent base directory — otherwise files get created in one place and looked for in another. I fixed this by explicitly setting `cwd` for every subprocess call.
>
> Also re-hit the same "profiles.yml doesn't exist on a fresh environment" issue from the GitHub Actions phase — confirming this is a recurring pattern whenever code runs on a new/ephemeral machine, not a one-off bug.
 