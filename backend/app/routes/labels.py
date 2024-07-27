from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
import pandas as pd
from app.services.label_service import create_labels
from io import BytesIO

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    columns = [
        'Auftragsnummer',
        'Annahmedatum_Uhrzeit1',
        'Notizen_Serviceberater',
        'Kundenname',
        'Kennzeichen'
    ]
    df = pd.read_csv(file.file, delimiter='\t', usecols=columns)
    output = BytesIO()
    create_labels(df, output)
    output.seek(0)
    return FileResponse(output, filename="Etiketten.pdf", media_type="application/pdf")