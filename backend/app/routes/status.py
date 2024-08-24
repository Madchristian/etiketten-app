from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse
import sqlite3
import os
from app.database import DB_PATH

router = APIRouter()

# Lade die Templates aus dem "backend/app/templates" Verzeichnis
templates = Jinja2Templates(directory="app/templates")

@router.get("/status")
async def get_status():
    # Erstelle eine neue Verbindung zur Datenbank mit DB_PATH
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT count FROM etiketten_count WHERE id = 1')
        row = cursor.fetchone()
        labels_count = row[0] if row else 0
        
        tmp_files_count = len(os.listdir("files"))
        
        cursor.execute('SELECT COUNT(*) FROM etiketten')
        etiketten_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(label_count) FROM processed_labels')
        processed_labels_count = cursor.fetchone()[0] or 0

    return JSONResponse(content={
        "labels_count": labels_count,
        "tmp_files_count": tmp_files_count,
        "etiketten_count": etiketten_count,
        "processed_labels_count": processed_labels_count
    })

@router.get("/status_page")
async def status_page(request: Request):
    return templates.TemplateResponse("status.html", {"request": request})