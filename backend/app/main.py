from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload_router  # Importiere den Router, wo du deinen APIRouter definiert hast

app = FastAPI()

# CORS Middleware konfigurieren
origins = [
    "http://localhost",
    "http://localhost:3000",
    # Füge weitere erlaubte Origins hier hinzu
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router einbinden
app.include_router(upload_router)