import glob
from datetime import datetime
import json

import duckdb as db
import pandas as pd

def connect():
    return db.connect("quakes.duckdb")

def find_latest_bronze_file():
    files = glob.glob("bronze/quakes_*.json")
    return sorted(files,reverse=True)[0]   

def read_data_from_bronze():
    try:
        filepath = find_latest_bronze_file()
        with open(filepath, "r") as f:
            data = json.load(f)

        if data is not None:
            return [json.dumps(r) for r in data['features']] 
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None


def bronze():
    rows = read_data_from_bronze()

    now = datetime.now()
    df = pd.DataFrame({
        "raw_json": rows,
        "ingested_at": now
    })

    con = connect()
    con.sql("CREATE SCHEMA IF NOT EXISTS bronze")
    con.sql("DROP TABLE IF EXISTS bronze.quakes")
    con.sql("CREATE TABLE IF NOT EXISTS bronze.quakes AS SELECT * FROM df")
    q = con.sql("SELECT COUNT(*) AS total_rows FROM bronze.quakes").fetchone()
    print(q)
    con.close()
 

bronze()