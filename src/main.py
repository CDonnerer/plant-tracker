"""My fun cloud function
"""
from datetime import date

import pandas as pd

from google.cloud import bigquery
from google.cloud import secretmanager
from googleapiclient.discovery import build

# TODO: logging.

SHEET_ID = "1LuHSWJIRXN3KEoimvAa_LlmKE1yGIiH_ClbBKsIN-7A"
SAMPLE_RANGE_NAME = "Form Responses 1"


def hello_world(event, context):
    print("Starting up the cloud function")

    print("Retrieving data from gsheets...")
    df = get_gsheets_data()

    print("Writing data to BQ...")
    pdf_to_bq(df)

    print("Creating watering report...")
    res = create_watering_report(df)

    print("Sending watering report...")
    send_watering_report(res)


def get_gsheets_data():
    service = build("sheets", "v4")
    sheet = service.spreadsheets()

    result = (
        sheet.values().get(spreadsheetId=SHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    )

    values = result.get("values", [])

    df = pd.DataFrame(values[1:], columns=values[0])
    df = clean_df(df)
    return df


def clean_df(df):
    df.to_csv("/tmp/plants.csv", index=False)
    df = pd.read_csv(
        "/tmp/plants.csv", parse_dates=["Timestamp"], infer_datetime_format=True
    )
    df.columns = (
        df.columns.str.replace(" ", "_")
        .str.replace(",", "")
        .str.replace("?", "", regex=False)
        .str.lower()
    )
    return df


def pdf_to_bq(df, table_id="plant-tracker-sandbox.plant_tracker.watering_history"):
    client = bigquery.Client(project="plant-tracker-sandbox")

    # dataset = client.create_dataset('plant_tracker', exists_ok=True)
    # table = dataset.table('watering_history')

    job_config = bigquery.job.LoadJobConfig(write_disposition="WRITE_TRUNCATE")

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    table = client.get_table(table_id)
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), table_id
        )
    )

def create_watering_report(df):
    df["watering_date"] = df["timestamp"].dt.date
    df["days_since_watering"] = date.today() - df["watering_date"]

    df["days_since_previous_watering"] = df.groupby("which_plant")["days_since_watering"].diff()

    res = df.groupby("which_plant").agg(
        last_watering=("days_since_watering", "min"),
        mean_days_between_watering=("days_since_previous_watering", "mean")
    )
    res["mean_days_between_watering"] = abs(res["mean_days_between_watering"].dt.days)
    return res


def send_watering_report(res):
    import sendgrid

    sc_client = secretmanager.SecretManagerServiceClient()

    name = "projects/687238585869/secrets/SENDGRID_API_KEY/versions/latest"
    response = sc_client.access_secret_version(name=name)
    sendgrid_api_key = response.payload.data.decode('UTF-8')

    sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)

    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email='christian.donnerer@gmail.com',
        to_emails='christian.donnerer@gmail.com',
        subject='Watering report',
        html_content=res.to_html()
    )

    response = sg.send(message)
    print(response.status_code, response.body, response.headers)


