from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.labels import router as labels_router  # Importiere den Router korrekt

app = FastAPI()

# CORS Middleware konfigurieren
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://backend:8000",
    "https://etiketten.cstrube.de",
    "https://etiketten.cstrube.de/upload/",
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
app.include_router(labels_router)