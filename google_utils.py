import os
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file("creds.json", scopes=SCOPES)
client = gspread.authorize(creds)

def append_to_sheet(spreadsheet_id, row):
    sheet = client.open_by_key(spreadsheet_id).sheet1
    sheet.append_row(row, value_input_option="USER_ENTERED")

def upload_file_to_drive(file_path):
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype="application/pdf")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return f"https://drive.google.com/file/d/{file['id']}/view"
