from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
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
import pandas as pd

router = APIRouter()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    upload_id = None
    file_location = None
    try:
        logger.info(f"Dateiname: {file.filename}")
        logger.info(f"Dateityp: {file.content_type}")

        # Maximal erlaubte Dateigröße und erlaubte Dateierweiterungen
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
        allowed_extensions = ['.csv', '.xlsx']  # Erlaubte Dateitypen

        # Dateierweiterung überprüfen
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            logger.error("Ungültiger Dateityp hochgeladen.")
            raise HTTPException(
                status_code=400,
                detail="Ungültiger Dateityp. Bitte laden Sie eine CSV- oder Excel-Datei hoch."
            )

        # Dateiinhalt in den Speicher lesen
        file_content = await file.read()
        file_size = len(file_content)
        logger.info(f"Dateigröße: {file_size} Bytes")

        if file_size > MAX_FILE_SIZE:
            logger.error("Datei überschreitet die maximale Größe.")
            raise HTTPException(
                status_code=400,
                detail="Die Datei ist zu groß. Maximale Dateigröße beträgt 10 MB."
            )

        # Dateiinhalt für die Validierung verwenden
        try:
            file_bytes = BytesIO(file_content)
            if file_extension == '.csv':
                df = pd.read_csv(file_bytes, sep='\t')
            elif file_extension == '.xlsx':
                df = pd.read_excel(file_bytes)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Dateityp wird nicht unterstützt."
                )

            if df.empty:
                logger.error("Die hochgeladene Datei enthält keine Daten.")
                raise HTTPException(
                    status_code=400,
                    detail="Die hochgeladene Datei ist leer."
                )

            # Erforderliche Spalten überprüfen
            required_columns = ['Auftragsnummer', 'Annahmedatum_Uhrzeit1', 'Notizen_Serviceberater', 'Reparaturumfang',
                                'Kundenname', 'Fertigstellungstermin', 'Terminart', 'Amtl. Kennzeichen',
                                'Direktannahme am Fzg.', 'Terminstatus', 'Modell']
            if not all(column in df.columns for column in required_columns):
                logger.error("Erforderliche Spalten fehlen in der Datei.")
                raise HTTPException(
                    status_code=400,
                    detail=f"Die Datei muss die folgenden Spalten enthalten: {', '.join(required_columns)}"
                )
        except Exception as e:
            logger.error(f"Fehler beim Lesen der Datei: {e}")
            raise HTTPException(
                status_code=400,
                detail="Die Datei konnte nicht gelesen werden. Stellen Sie sicher, dass es sich um eine gültige CSV- oder Excel-Datei handelt."
            )

        # Datei speichern
        file_id = str(uuid4())
        file_location = f"{UPLOAD_DIR}/{file_id}{file_extension}"

        with open(file_location, "wb+") as file_object:
            file_object.write(file_content)
        logger.info(f"Datei hochgeladen und gespeichert unter: {file_location}")

        # Daten in die Datenbank laden
        data_loader = DataLoader(db_path)
        upload_id = data_loader.load_data(file_location)
        logger.info("Daten in die Datenbank %s geladen", db_path)

        # Daten vorverarbeiten
        DataPreprocessor.preprocess_data(db_path)
        logger.info("Datenbank vorverarbeitet")

        # Sortierte Daten abrufen
        data_retriever = DataRetriever(db_path)
        df = data_retriever.get_sorted_data(upload_id)

        if df.empty:
            logger.error("Keine Daten vorhanden, um Etiketten zu erstellen.")
            raise HTTPException(
                status_code=400,
                detail="Keine gültigen Daten in der Datei gefunden."
            )

        logger.info("Daten aus der Datenbank sortiert:")
        logger.info(df.head())

        # PDF erstellen
        output = BytesIO()
        try:
            create_labels(df, output)
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der PDF: {e}")
            raise HTTPException(
                status_code=500,
                detail="Fehler beim Erstellen der PDF."
            )

        output.seek(0)

        # Anzahl der verarbeiteten Labels loggen
        process_logger = ProcessLogger(db_path)
        process_logger.log_processed_labels(len(df))

        # Erfolgreiche Rückgabe der PDF
        headers = {
            'Content-Disposition': f'attachment; filename="{datetime.now().strftime("%Y%m%d_%H%M%S")}_Terminetiketten.pdf"'
        }
        return StreamingResponse(output, media_type="application/pdf", headers=headers)

    except HTTPException as e:
        # Fehler dem Benutzer in verständlicher Form zurückgeben
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})

    except Exception as e:
        # Allgemeine Fehlerbehandlung
        logger.error(f"Unerwarteter Fehler: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": "Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut."}
        )

    finally:
        # Datenbankbereinigung und temporäre Datei löschen
        if upload_id:
            data_deleter = DataDeleter(db_path)
            data_deleter.delete_data_by_upload_id(upload_id)
            logger.info(f"Einträge mit upload_id '{upload_id}' aus der Datenbank gelöscht")

        if file_location and os.path.exists(file_location):
            os.remove(file_location)
            logger.info(f"Temporäre Datei '{file_location}' gelöscht")