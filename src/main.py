"""My fun cloud function
"""
import pandas as pd

from google.cloud import bigquery
from googleapiclient.discovery import build

# TODO: logging.

SHEET_ID = "1LuHSWJIRXN3KEoimvAa_LlmKE1yGIiH_ClbBKsIN-7A"
SAMPLE_RANGE_NAME = 'R1C1:R2C2'


def hello_world(event, context):
    print("Starting up the cloud function")

    print("Retrieving data from gsheets...")
    df = get_gsheets_data()

    print("Writing data from BQ...")
    pdf_to_bq(df)



def get_gsheets_data():
    service = build('sheets', 'v4')
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=SHEET_ID,
        range=SAMPLE_RANGE_NAME
    ).execute() 

    values = result.get('values', [])

    df = pd.DataFrame(values[1:], columns=values[0])
    df = clean_df(df)
    return df

def clean_df(df):
    df.to_csv("plants.csv", index=False)
    df = pd.read_csv(
        "plants.csv", 
        parse_dates=["Timestamp"], 
        infer_datetime_format=True
    )
    df.columns = (
        df.columns
        .str.replace(' ', '_')
        .str.replace(',', '')
        .str.replace('?','', regex=False)
        .str.lower()
    )
    return df


def pdf_to_bq(
    df, 
    table_id="plant-tracker-sandbox.plant_tracker.watering_history"
):
    client = bigquery.Client(project="plant-tracker-sandbox")
  
    # dataset = client.create_dataset('plant_tracker', exists_ok=True)
    # table = dataset.table('watering_history')

    job_config = bigquery.job.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )

    job = client.load_table_from_dataframe(
        df, table_id, job_config=job_config
    ) 
    job.result()
    table = client.get_table(table_id)
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), table_id
        )
    )


