from fastapi import Request
from .database import cursor, conn

async def add_labels_counter(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/upload/" and response.status_code == 200:
        cursor.execute('UPDATE etiketten_count SET count = count + 1 WHERE id = 1')
        conn.commit()
    return response