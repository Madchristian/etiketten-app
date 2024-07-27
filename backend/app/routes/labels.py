from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
import pandas as pd
from app.services.label_service import create_labels
from io import BytesIO
from uuid import uuid4
import os

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
        'Kennzeichen'
    ]
    df = pd.read_csv(file_location, delimiter='\t', usecols=columns)

    # Erstelle die Labels und speichere sie im BytesIO-Objekt
    output = BytesIO()
    create_labels(df, output)
    output.seek(0)

    # Lösche die temporäre Datei
    os.remove(file_location)

    return FileResponse(output, filename="Etiketten.pdf", media_type="application/pdf")