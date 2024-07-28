from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
from app.services.label_service import create_labels
from io import BytesIO
from uuid import uuid4
import os
from datetime import datetime
from ..database import load_data_to_db, get_sorted_data, delete_data_by_upload_id, db_path, log_processed_labels
import logging

router = APIRouter()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Generiere eine eindeutige ID für diese Datei
    file_id = str(uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_location = f"{UPLOAD_DIR}/{file_id}{file_extension}"

    # Lese die Datei und speichere sie temporär
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    logger.info(f"Datei hochgeladen und gespeichert unter: {file_location}")

    # Lade die Daten in die Datenbank und erhalte die upload_id
    upload_id = load_data_to_db(file_location, db_path)
    logger.info(f"Daten in die Datenbank geladen mit upload_id: {upload_id}")

    # Sortiere die Daten aus der Datenbank
    df = get_sorted_data(db_path, upload_id)
    logger.info(f"Erste Zeilen der sortierten DataFrame:")
    logger.info(df.head())

    # Erstelle die Labels und speichere sie im BytesIO-Objekt
    output = BytesIO()
    create_labels(df, output)
    output.seek(0)

    # Lösche die Einträge aus der Datenbank und die temporäre Datei
    delete_data_by_upload_id(db_path, upload_id)
    os.remove(file_location)
    logger.info(f"Einträge mit upload_id '{upload_id}' aus der Datenbank gelöscht und temporäre Datei '{file_location}' gelöscht")

    # Logge die Anzahl der verarbeiteten Labels
    log_processed_labels(db_path, len(df))

    # Verwende StreamingResponse, um die PDF-Datei zurückzugeben
    headers = {
        'Content-Disposition': f'attachment; filename="{datetime.now().strftime("%Y%m%d_%H%M%S")}_Terminetiketten.pdf"'
    }
    return StreamingResponse(output, media_type="application/pdf", headers=headers)