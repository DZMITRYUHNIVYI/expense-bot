import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "creds.json"

def get_google_services():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    sheets_service = gspread.authorize(creds)
    drive_service = build("drive", "v3", credentials=creds)
    return sheets_service, drive_service

def append_to_sheet(spreadsheet_id, row):
    sheets_service, _ = get_google_services()
    sheet = sheets_service.open_by_key(spreadsheet_id).sheet1
    sheet.append_row(row, value_input_option="USER_ENTERED")

def upload_file_to_drive(file_path, folder_id=None):
    _, drive_service = get_google_services()
    file_metadata = {"name": os.path.basename(file_path)}
    if folder_id:
        file_metadata["parents"] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return f"https://drive.google.com/file/d/{uploaded_file['id']}/view"

def extract_file_info(file_path):
    return os.path.splitext(file_path)[1][1:].lower()

def process_voice(voice_path, spreadsheet_id):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    comment = f"Голосовое сообщение {now}"
    link = upload_file_to_drive(voice_path)
    append_to_sheet(spreadsheet_id, [now, "", "", "Голос", "", comment, "voice", link])
    return True