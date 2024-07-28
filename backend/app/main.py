from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from .routes.labels import router as labels_router
from .routes.status import router as status_router
from .routes.health import router as health_router
from .database import conn
from .middleware import add_labels_counter
from .config import CORS_ORIGINS

app = FastAPI()

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
    for filename in os.listdir("files"):
        file_path = os.path.join("files", filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
    conn.close()