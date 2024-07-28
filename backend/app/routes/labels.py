from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
from app.services.label_service import create_labels
from io import BytesIO
from uuid import uuid4
import os
from datetime import datetime

router = APIRouter()

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

    # Lese die Datei mit Pandas und wähle die gewünschten Spalten aus
    columns = [
        'Auftragsnummer',
        'Annahmedatum_Uhrzeit1',
        'Notizen_Serviceberater',
        'Kundenname',
        'Fertigstellungstermin',
        'Terminart',
        'Amtl. Kennzeichen'
    ]
    df = pd.read_csv(file_location, delimiter='\t', usecols=columns)

    # Erstelle die Labels und speichere sie im BytesIO-Objekt
    output = BytesIO()
    create_labels(df, output)
    output.seek(0)

    # Lösche die temporäre Datei
    os.remove(file_location)

    # Verwende StreamingResponse, um die PDF-Datei zurückzugeben
    headers = {
        'Content-Disposition': f'attachment; filename="{datetime.now().strftime("%Y%m%d_%H%M%S")}_Terminetiketten.pdf"'
    }
    return StreamingResponse(output, media_type="application/pdf", headers=headers)