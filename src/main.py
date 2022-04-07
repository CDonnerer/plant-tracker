"""My fun cloud function
"""
from googleapiclient.discovery import build

# TODO: logging.

SHEET_ID = "1LuHSWJIRXN3KEoimvAa_LlmKE1yGIiH_ClbBKsIN-7A"
SAMPLE_RANGE_NAME = 'R1C1:R2C2'


def hello_world(event, context):
    print("Starting up the cloud function")

    service = build('sheets', 'v4')
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=SHEET_ID,
        range=SAMPLE_RANGE_NAME
    ).execute() 

    print(result)

