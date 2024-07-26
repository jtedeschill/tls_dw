from dotenv import load_dotenv
import os
from etl.bullhorn import BullhornClient
from etl.etl.hubspot_etl import HubSpot
import pandas as pd

from tasks import bullhorn_tasks

import duckdb

load_dotenv()

con = duckdb.connect()


BH = BullhornClient(
    os.getenv("BH_USERNAME"),
    os.getenv("BH_PASSWORD"),
    os.getenv("BH_CLIENT_ID"),
    os.getenv("BH_CLIENT_SECRET"),
)
BH.authenticate()


for task, params in bullhorn_tasks.items():
    data = BH.make_request(
        params["endpoint"],
        params["fields"],
        params["query"],
        params["count"],
        params["start"],
    )
    df = pd.json_normalize(data)
    
    # transform the data
    print(df.head())

    try:    
        
        for column, operation in params["transform_map"].items():
            if callable(operation):
                df[column] = df[column].apply(operation)
            else:
                df[column] = df[column].astype(operation)


        df = df.rename(columns=params["rename_map"])

        df.to_csv(f"{params['endpoint']}.csv", index = False)

    except Exception as e:
        print(f"Error transforming data: {e}")

