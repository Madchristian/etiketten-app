from starlette.config import Config

config = Config(".env")

CORS_ORIGINS = config("CORS_ORIGINS", cast=lambda v: [s.strip() for s in v.split(",")])