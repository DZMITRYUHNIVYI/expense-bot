import fitz  # PyMuPDF
from google_utils import append_to_sheet, upload_file_to_drive
from datetime import datetime

def process_ticket_file(file_path, spreadsheet_id):
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()

        lines = text.split("\n")
        date = extract_date(lines)
        names = extract_names(lines)
        price = extract_price(lines)
        route = extract_route(lines)

        if not date or not names or not price or not route:
            return False

        per_person = round(price / len(names), 2)
        drive_link = upload_file_to_drive(file_path)

        for name in names:
            row = [date, "", name, "Билеты", per_person, "pdf", drive_link]
            append_to_sheet(spreadsheet_id, row)

        return True
    except Exception as e:
        print("Ошибка при обработке билета:", e)
        return False

def extract_date(lines):
    for line in lines:
        if any(m in line for m in ["2025", "2024"]):
            try:
                parts = line.strip().split()
                for p in parts:
                    if "." in p and len(p) == 10:
                        return p
            except:
                continue
    return datetime.today().strftime("%d.%m.%Y")

def extract_names(lines):
    keywords = ["Name", "Pasajero", "Fahrer"]
    names = []
    for line in lines:
        if any(k in line for k in keywords):
            parts = line.replace("Name:", "").split()
            names.extend([p for p in parts if p.istitle()])
    return list(set(names)) or ["Билеты"]

def extract_price(lines):
    for line in lines:
        if "Total price" in line or "EUR" in line:
            nums = [s.replace(",", ".") for s in line.split() if s.replace(",", ".").replace(".", "", 1).isdigit()]
            if nums:
                return float(nums[-1])
    return 0.0

def extract_route(lines):
    for line in lines:
        if "→" in line or "to" in line.lower():
            return line.strip()
    return "Маршрут не найден"
