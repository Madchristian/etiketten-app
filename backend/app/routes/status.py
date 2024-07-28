from fastapi import APIRouter
from starlette.responses import JSONResponse
import os
from ..database import cursor

router = APIRouter()

@router.get("/status")
async def get_status():
    # Zähler für etiketten_count abfragen
    cursor.execute('SELECT count FROM etiketten_count WHERE id = 1')
    row = cursor.fetchone()
    labels_count = row[0] if row else 0
    
    # Anzahl der temporären Dateien abfragen
    tmp_files_count = len(os.listdir("files"))
    
    # Anzahl der Einträge in der etiketten-Tabelle abfragen
    cursor.execute('SELECT COUNT(*) FROM etiketten')
    etiketten_count = cursor.fetchone()[0]
    
    return JSONResponse(content={"labels_count": labels_count, "tmp_files_count": tmp_files_count, "etiketten_count": etiketten_count})