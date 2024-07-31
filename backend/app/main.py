from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import logging
from app.routes.labels import router as labels_router
from app.routes.status import router as status_router
from app.routes.health import router as health_router
from app.database import DatabaseInitializer, DB_PATH
from app.middleware import add_labels_counter
from app.config import CORS_ORIGINS

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

def create_app():
    app = FastAPI()

    # Logging konfigurieren
    logger = setup_logging()

    # Datenbank initialisieren
    DatabaseInitializer.initialize(DB_PATH)

    # CORS Middleware konfigurieren
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Middleware hinzufügen
    app.middleware("http")(add_labels_counter)

    # Router einbinden
    app.include_router(labels_router)
    app.include_router(status_router)
    app.include_router(health_router)

    @app.on_event("shutdown")
    async def shutdown_event():
        # Temporäre Dateien löschen
        logger.info("Lösche temporäre Dateien...")
        for filename in os.listdir("files"):
            file_path = os.path.join("files", filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"Failed to delete {file_path}. Reason: {e}")
        logger.info("Datenbankverbindung geschlossen.")

    # Start Logging
    logger.info("Applikation gestartet.")
    return app

app = create_app()