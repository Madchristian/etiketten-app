from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from io import BytesIO
from uuid import uuid4
import os
from datetime import datetime
from app.services.label_service import create_labels
from app.utils.data_loader import DataLoader
from app.utils.data_retriever import DataRetriever
from app.utils.data_deleter import DataDeleter
from app.utils.process_logger import ProcessLogger
from app.utils.data_preprocessor import DataPreprocessor
from app.database import DB_PATH as db_path
import logging
import sqlite3

router = APIRouter()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_label_config(config_name, db_path):
    """
    Lädt die Etikettenkonfiguration aus der Datenbank.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM etiketten_config WHERE name = ?", (config_name,))
        row = cursor.fetchone()
        if row:
            return {
                'label_width': row[2] * mm,
                'label_height': row[3] * mm,
                'margin_left': row[4] * mm,
                'margin_top': row[5] * mm,
                'h_space': row[6] * mm,
                'v_space': row[7] * mm,
                'rows': row[8],
                'columns': row[9],
                'max_name_length': row[10]
            }
        else:
            raise ValueError(f"Label config '{config_name}' not found")

@router.get("/labels")
async def get_labels():
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM etiketten_config")
            labels = cursor.fetchall()
        return {"labels": [label[0] for label in labels]}
    except Exception as e:
        return {"error": str(e)}

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"Dateiname: {file.filename}")
        logger.info(f"Dateityp: {file.content_type}")
        logger.info(f"Dateigröße: {file.size}")
        
        file_id = str(uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_location = f"{UPLOAD_DIR}/{file_id}{file_extension}"

        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        logger.info(f"Datei hochgeladen und gespeichert unter: {file_location}")

        data_loader = DataLoader(db_path)
        upload_id = data_loader.load_data(file_location)
        logger.info("Daten in die Datenbank %s geladen", db_path)

        DataPreprocessor.preprocess_data(db_path)
        logger.info("Datenbank vorverarbeitet")
        
        data_retriever = DataRetriever(db_path)
        df = data_retriever.get_sorted_data(upload_id)
        logger.info("Daten aus der Datenbank sortiert:")
        logger.info(df.head())

        # Lade die Etikettenkonfiguration
        config_name = "Standardetikett"  # Dies könnte aus einem Parameter kommen oder in der Datenbank gespeichert sein
        label_config = load_label_config(config_name, db_path)

        output = BytesIO()
        create_labels(df, output, label_config)
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