import os
import fitz  # PyMuPDF
from google_utils import append_to_sheet, upload_file_to_drive
from datetime import datetime

# Словарь объектов по сотрудникам
OBJECTS = {
    "Hradouski Andrei": "INGOLSTADT",
    "Siarhei Vaskevich": "INGOLSTADT",
    "Siarhei Peahko": "INGOLSTADT",
    "Pavel Vaitushka": "INGOLSTADT",
    "Andrei Padzialinski": "INGOLSTADT",
    "Uladzimir Astapchuk": "INGOLSTADT",
    "Andrei Palauchenia": "INGOLSTADT",
    "Ilya Zhuk": "INGOLSTADT",
    "Siarhei Khmurovich": "INGOLSTADT",
    "Stsiatsko Anton": "INGOLSTADT",
    "SHATSILA SIARHEI": "AACHEN",
    "KULIAKIN ANDREI": "AACHEN",
    "KAZAKEVICH SIARHEI": "AACHEN",
    "BIADNIUK PIOTR": "AACHEN",
    "MARKAU ALIAKSANDR": "AACHEN",
    "NECHAYEU IHAR": "HLS",
    "BYCHUK ALEH": "HLS",
    "KUNITSKI VITALI": "HLS",
    "MIKUTSKI VALERY": "HLS",
    "MAKARAU MIKHAIL": "HLS",
    "ASIPOVICH ANDREI": "HLS",
    "KALESNIKAU ALIAKSEI": "HLS",
    "SINKEVICH YURY": "HLS",
    "MATSUKEVICH MIKITA": "FRA33",
    "MAMEDAU ANDREI": "FRA33",
    "STEPCHUK DZMYTRO": "FRA33",
    "Khvat Artur": "BOCHUM",
    "Buinavets Vasili": "BOCHUM",
    "Kazakevich Vitali": "BOCHUM",
    "Zasutski Maksim": "BOCHUM",
    "Sadouski Dzmitry": "BOCHUM",
    "Khojiev Bokhodir": "BOCHUM",
    "Pihaleu Dzmitry": "BOCHUM",
    "Palamarchyk Oleksandr": "BOCHUM",
    "SHUTKEVICH PAVIAL": "DORTMUND",
    "CHUDZILOUSKI DZIANIS": "DORTMUND",
    "POLAK ARKADIUSZ": "DORTMUND",
    "SIAMIONAU SIARHEI": "REGENSBURG",
    "BARYSAU SIARHEI": "REGENSBURG",
    "VERETEYKO ALEKSANDER": "REGENSBURG",
    "MAROZAU MAKSIM": "REGENSBURG",
    "PRYKHODZKA YAUHEN": "REGENSBURG",
    "DZIAZMYNCKI MIKALAI": "REGENSBURG",
    "KANIASHIN RUSLAN": "REGENSBURG",
    "SEVASTSYAN SIARHEI": "REGENSBURG",
    "DZEWANOUSKI ULADZISLAU": "REGENSBURG",
    "ZENCHYK DZMITRY": "REGENSBURG",
    "RIAZANOV YEVHENII": "REGENSBURG",
    "SADOUSKI SIARHEI": "REGENSBURG",
    "ZALEUSKI DZMITRY": "REGENSBURG",
    "LISAI SIARHEI": "REGENSBURG",
    "KALKO DZMITRY": "REGENSBURG",
    "AUSEICHYK MAKSIM": "REGENSBURG",
    "BOLOG SAHOS": "REGENSBURG",
    "VARADI OLEKSANDR": "REGENSBURG",
    "VASILCHYK HENADZI": "REGENSBURG",
    "GOLUBEV IGOR": "REGENSBURG",
    "TSYBULSKI YURY": "REGENSBURG",
    "BIARESHCHANKA IHAR": "REGENSBURG",
    "VASEICHYK VLADISLAV": "REGENSBURG",
    "SHMYHALIOU ANDREI": "REGENSBURG",
    "SAIDASHAU VIACHESLAU": "REGENSBURG",
    "BAIHOT ALEH": "REGENSBURG",
    "NERUSHAU ALIAKSANDR": "REGENSBURG",
    "MALAK ROBERT": "REGENSBURG",
    "KRASNIATSOU DZIANIS": "REGENSBURG",
    "KULISHEVICH DZMITRY": "REGENSBURG",
    "KADZEVICH MAKSIM": "REGENSBURG",
    "DRABOVICH RAMAN": "REGENSBURG",
    "TKACH SERGEY": "PWC Hamburg",
    "LISICINAS VADIMAS": "PWC Hamburg",
    "HORBATIUK VASYL": "PWC Hamburg",
    "TARASENCO SERGHEI": "PWC Hamburg",
    "LEWANDOWSKI MAREK": "PWC Hamburg",
    "RUBTSEVICH PAVEL": "COLT",
    "NAVICHENKA MIKITA": "COLT",
    "NAKLADOVICH ANDREI": "COLT",
    "KIRKEVICH SIARHEI": "Viktor 3",
    "ZHARKO IHAR": "Viktor 3",
    "HAURYLCHUK VIKTAR": "Viktor 3",
    "AMELKA KIRYL": "Viktor 3",
    "MAROZ MAKSIM": "Viktor 3",
    "HAURYLCHUK VLAD": "Viktor 3",
    "SHARIPOV ANATOLII": "Viktor 3",
    "KULAK DZMITRY": "Viktor 3",
    "KHALETSKI PAVEL": "Viktor 3",
    "SHCHUKA DZMITRY": "Viktor 3",
    "LUCHKO ALEH": "Viktor 3",
    "YANKOUSKI DZMITRY": "Viktor 3",
    "YUTSKEVICH MIKHAIL": "Viktor 3",
    "VAUCHOK STANISLAU": "Viktor 3",
    "HUTSKO YURY": "Viktor 3",
    "VIDLOUSKI VITALI": "Viktor 3",
    "ASIPOVICH ANDREI": "Viktor 3",
    "SVIARHUN ANDREI": "Viktor 3"
}

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
            obj = OBJECTS.get(name.upper(), "Билеты")
            row = [date, obj, name, "Билеты", per_person, "pdf", drive_link]
            append_to_sheet(spreadsheet_id, row)

        return True
    except Exception as e:
        print("Ошибка при обработке билета:", e)
        return False

def extract_date(lines):
    for line in lines:
        if any(y in line for y in ["2025", "2024"]):
            parts = line.strip().split()
            for p in parts:
                if "." in p and len(p) == 10:
                    return p
    return datetime.today().strftime("%d.%m.%Y")

def extract_names(lines):
    keywords = ["Name", "Pasajero", "Fahrer"]
    names = []
    for line in lines:
        if any(k in line for k in keywords):
            parts = line.replace("Name:", "").split()
            names.append(" ".join([p for p in parts if p.istitle()]))
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
