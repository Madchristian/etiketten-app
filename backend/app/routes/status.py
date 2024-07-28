from fastapi import APIRouter
from starlette.responses import JSONResponse
import os
from ..database import cursor

router = APIRouter()

@router.get("/status")
async def get_status():
    cursor.execute('SELECT count FROM etiketten_count WHERE id = 1')
    row = cursor.fetchone()
    labels_count = row[0] if row else 0
    tmp_files_count = len(os.listdir("files"))
    return JSONResponse(content={"labels_count": labels_count, "tmp_files_count": tmp_files_count})