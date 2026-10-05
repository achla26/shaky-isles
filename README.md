# Shaky Isles 🏔️
Hourly NZ earthquake pipeline: GeoNet API → Parquet → DuckDB → dbt marts.

## Architecture
GeoNet API → scripts/fetch_quakes.py → data/bronze/ → DuckDB → quake_dbt/ → GitHub Actions ⏰


## Stack
Python · DuckDB · dbt · Docker · Airflow · GitHub Actions

## How to Run

**1. Clone the repo and create a virtual environment**:
   ```
   git clone https://github.com/achla26/shaky-isles.git
   cd shaky-isles
   python -m venv venv
   venv\Scripts\activate    
   ```

**2. Install dependencies:**
   ```
   pip install -r requirements.txt 
   ```

**3. Run the pipeline manually:**
   ```
   python scripts/fetch_quakes.py
   python scripts/connect_db.py
   cd quake_dbt
   dbt run
   dbt test
   ```

**4. Or let it run automatically —** GitHub Actions triggers this every hour (see `.github/workflows/quake.yml`).


## What I Learned
1. **Phase 1 (Extract):** Raw data should be stored exactly as received, without modification — I initially extracted only select fields and lost part of the raw structure, then corrected it to store the full response.
2. **Phase 2 (Load):** Store raw data as one row per record with a unique ID and an `ingested_at` timestamp — the unique ID enables idempotency (no duplicates on re-run), and the timestamp supports future watermark-based loading.
3. **Phase 3 (Transform):** Connected raw data to dbt using `source()`, built models with `ref()`, and used `json_extract_string()` to parse nested JSON into typed columns — plus added schema tests (`not_null`, `unique`).
4. **Phase 4A (CI/CD):** Automated the pipeline with GitHub Actions, including solving the classic "profiles.yml doesn't exist on a fresh machine" issue by generating it at runtime.
5. **Phase 4B (Orchestration):** Built and ran an Airflow DAG locally using Docker, learning how task dependencies, retries, and environment differences (missing dependencies, working directories) affect a real pipeline.