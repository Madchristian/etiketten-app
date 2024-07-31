from fastapi import APIRouter
from starlette.responses import JSONResponse
from app.database import cursor

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        cursor.execute('SELECT 1')
        return JSONResponse(content={"status": "healthy"})
    except Exception as e:
        return JSONResponse(content={"status": "unhealthy", "error": str(e)}, status_code=500)