from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
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

def delete_temp_file(file_location):
    if os.path.exists(file_location):
        os.remove(file_location)

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Prüfen, ob die Datei eine .txt-Datei ist
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Nur .txt Dateien sind erlaubt.")
    
    # Prüfen, ob die Datei kleiner als 300 KB ist
    if file.size > 300 * 1024:
        raise HTTPException(status_code=400, detail="Die Datei darf maximal 300 KB groß sein.")

    # Generiere eine eindeutige ID für diese Datei
    file_id = str(uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_location = f"{UPLOAD_DIR}/{file_id}{file_extension}"

    try:
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
    finally:
        # Lösche die temporäre Datei
        delete_temp_file(file_location)

    # Aktuelles Datum für den Dateinamen
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Verwende StreamingResponse, um die PDF-Datei zurückzugeben
    headers = {
        'Content-Disposition': f'attachment; filename="{current_date}_Terminetiketten.pdf"'
    }
    return StreamingResponse(output, media_type="application/pdf", headers=headers)