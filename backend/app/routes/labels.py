from fastapi import APIRouter, File, UploadFile, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO
from uuid import uuid4
import os
from datetime import datetime
from app.services.label_service import create_labels
from app.utils.data_loader import DataLoader
from app.utils.data_retriever import DataRetriever
from app.utils.data_deleter import DataDeleter
from app.utils.process_logger import ProcessLogger
from app.database import DB_PATH as db_path
import logging

router = APIRouter()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class LabelPosition(BaseModel):
    row: int
    col: int

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), start_position: LabelPosition = Body(...)):
    try:
        file_id = str(uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_location = f"{UPLOAD_DIR}/{file_id}{file_extension}"

        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        logger.info(f"Datei hochgeladen und gespeichert unter: {file_location}")

        data_loader = DataLoader(db_path)
        upload_id = data_loader.load_data(file_location)
        logger.info("Daten in die Datenbank %s geladen", db_path)

        data_retriever = DataRetriever(db_path)
        df = data_retriever.get_sorted_data(upload_id)
        logger.info("Daten aus der Datenbank sortiert:")
        logger.info(df.head())

        output = BytesIO()
        create_labels(df, output, start_position.row, start_position.col)
        output.seek(0)

        data_deleter = DataDeleter(db_path)
        data_deleter.delete_data_by_upload_id(upload_id)
        os.remove(file_location)
        logger.info(f"Einträge mit upload_id '{upload_id}' aus der Datenbank gelöscht und temporäre Datei '{file_location}' gelöscht")

        process_logger = ProcessLogger(db_path)
        process_logger.log_processed_labels(len(df))

        headers = {
            'Content-Disposition': f'attachment; filename="{datetime.now().strftime("%Y%m%d_%H%M%S")}_Terminetiketten.pdf"'
        }
        return StreamingResponse(output, media_type="application/pdf", headers=headers)
    
    except Exception as e:
        logger.error("Fehler beim Verarbeiten der Datei: %s", e)
        return {"error": "Fehler beim Verarbeiten der Datei"}