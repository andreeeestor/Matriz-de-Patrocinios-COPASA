import os
from pydantic_settings import BaseSettings
from functools import lru_cache

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkey123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MODELO_PLANILHA: str = os.path.join(BASE_DIR, "modelo.xlsx")

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()