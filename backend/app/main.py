from fastapi import FastAPI
from app.routes import labels

app = FastAPI()

app.include_router(labels.router)