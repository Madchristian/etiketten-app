from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from app.services.label_service import create_labels
from app.database import load_data_to_db, get_sorted_data, delete_data_by_upload_id
from io import BytesIO
from uuid import uuid4
import os
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

db_path = "/app/etiketten.db"  # Füge den Datenbankpfad hier hinzu

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Generiere eine eindeutige ID für diese Datei
    file_id = str(uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_location = f"{UPLOAD_DIR}/{file_id}{file_extension}"

    # Lese die Datei und speichere sie temporär
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Lade die Datei in die Datenbank
    upload_id = load_data_to_db(file_location, db_path)

    # Daten aus der Datenbank sortiert abrufen
    df = get_sorted_data(db_path, upload_id)

    # Debugging-Ausgabe der ersten Zeilen der sortierten DataFrame
    print("Erste Zeilen der sortierten DataFrame:")
    print(df.head())

    # Erstelle die Labels und speichere sie im BytesIO-Objekt
    output = BytesIO()
    create_labels(df, output)
    output.seek(0)

    # Lösche die Einträge aus der Datenbank
    delete_data_by_upload_id(db_path, upload_id)
    print(f"Einträge mit upload_id '{upload_id}' aus der Datenbank gelöscht")

    # Lösche die temporäre Datei
    os.remove(file_location)
    print(f"Temporäre Datei '{file_location}' gelöscht")

    # Verwende StreamingResponse, um die PDF-Datei zurückzugeben
    headers = {
        'Content-Disposition': f'attachment; filename="{datetime.now().strftime("%Y%m%d_%H%M%S")}_Terminetiketten.pdf"'
    }
    return StreamingResponse(output, media_type="application/pdf", headers=headers)