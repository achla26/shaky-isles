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
            return [(r['properties']['publicID'], json.dumps(r)) for r in data['features']] 
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None


def bronze():
    rows = read_data_from_bronze()

    now = datetime.now()
    df = pd.DataFrame({
        "quake_id": [row[0] for row in rows],   
        "raw_json": [row[1] for row in rows],  
        "ingested_at": now
    })

    con = connect()
    con.sql("CREATE SCHEMA IF NOT EXISTS bronze") 
    con.sql("""
        CREATE TABLE IF NOT EXISTS bronze.quakes (
            quake_id VARCHAR,
            raw_json VARCHAR,
            ingested_at TIMESTAMP
        )
    """)
    con.sql("""
        INSERT INTO bronze.quakes
        SELECT * FROM df
        WHERE quake_id NOT IN (SELECT quake_id FROM bronze.quakes)
    """) 

    q = con.sql("SELECT COUNT(*) AS total_rows FROM bronze.quakes").fetchone()
    print(q)
    con.close()
 

bronze() 