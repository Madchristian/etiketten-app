from fastapi import APIRouter
from starlette.responses import JSONResponse
import os
from ..database import cursor, db_path

router = APIRouter()

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

    return JSONResponse(content={"labels_count": labels_count, "tmp_files_count": tmp_files_count})

