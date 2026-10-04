# Shaky Isles 🏔️
Hourly NZ earthquake pipeline: GeoNet API → Parquet → DuckDB → dbt marts.

## Architecture
GeoNet API → scripts/fetch_quakes.py → data/bronze/ → DuckDB → quake_dbt/ → GitHub Actions ⏰

## Stack
Python · DuckDB · dbt · GitHub Actions