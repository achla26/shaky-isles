import requests
import json
import os
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

url = "https://api.geonet.org.nz/quake?MMI=3"

def fetch_data_from_api(url):
    try:
        response = requests.get(url , timeout=30)
        response.raise_for_status()
        data= response.json()

        print(data.keys())

        print(f"Total Length of data {len(data['features'])}")
 
        return data
    except Exception as  e:
        print(f"API ERROR: {str(e)}")
        return None

def bronze_raw_data(data):
    if data is not None:
        try:
            # create bronze folder if not exists
            os.makedirs(name="bronze" , exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            filepath = f"bronze/quakes_{timestamp}.json"

            with open(filepath , "w" ,encoding="utf-8") as f:
                json.dump(data , f ,indent=2)

            print(f"Saved to {filepath}")    
        except Exception as  e:
            print(f"BRONZE ERROR: {str(e)}")
    else:
        print("No data to save - skipping bronze write")

def parquet_format(data , fp):
    df = pd.DataFrame(data)
    # Convert the DataFrame to an Arrow Table

    tbl = pa.Table.from_pandas(df)
    
    # Write the Arrow Table to a Parquet file
    pq.write_table(tbl , fp)
 

if __name__ == "__main__":
    data = fetch_data_from_api(url)
    bronze_raw_data(data)

 