from fastapi import APIRouter, Request
from starlette.responses import JSONResponse
from fastapi.templating import Jinja2Templates

import os
from app.database import cursor, DB_PATH

router = APIRouter()

# Lade die Templates aus dem "backend/app/templates" Verzeichnis
templates = Jinja2Templates(directory="app/templates")


@router.get("/status")
async def get_status():
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
    # Die Daten werden vom JavaScript im Template geladen
    return templates.TemplateResponse("status.html", {"request": request})