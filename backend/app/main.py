# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes.labels import router as labels_router
from starlette.config import Config
from starlette.responses import JSONResponse
import os
import sqlite3
from datetime import datetime

# Konfigurationsdatei laden
config = Config(".env")

# Lade die CORS-Origins aus der .env Datei
cors_origins = config("CORS_ORIGINS", cast=lambda v: [s.strip() for s in v.split(",")])

app = FastAPI()

# SQLite Verbindung herstellen
conn = sqlite3.connect('etiketten.db', check_same_thread=False)
cursor = conn.cursor()

# Tabelle erstellen, falls nicht vorhanden
cursor.execute('''CREATE TABLE IF NOT EXISTS etiketten_count (
                  id INTEGER PRIMARY KEY,
                  count INTEGER NOT NULL DEFAULT 0
                )''')
conn.commit()

# Initialisiere den Zähler, falls nicht vorhanden
cursor.execute('SELECT count FROM etiketten_count WHERE id = 1')
row = cursor.fetchone()
if row is None:
    cursor.execute('INSERT INTO etiketten_count (id, count) VALUES (1, 0)')
    conn.commit()

# CORS Middleware konfigurieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router einbinden
app.include_router(labels_router)

@app.middleware("http")
async def add_labels_counter(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/upload/" and response.status_code == 200:
        cursor.execute('UPDATE etiketten_count SET count = count + 1 WHERE id = 1')
        conn.commit()
    return response

@app.get("/status")
async def get_status():
    cursor.execute('SELECT count FROM etiketten_count WHERE id = 1')
    row = cursor.fetchone()
    labels_count = row[0] if row else 0
    tmp_files_count = len(os.listdir("files"))
    return JSONResponse(content={"labels_count": labels_count, "tmp_files_count": tmp_files_count})

@app.get("/health")
async def health_check():
    try:
        cursor.execute('SELECT 1')
        return JSONResponse(content={"status": "healthy"})
    except Exception as e:
        return JSONResponse(content={"status": "unhealthy", "error": str(e)}, status_code=500)

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