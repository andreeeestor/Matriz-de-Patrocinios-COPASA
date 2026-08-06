from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkey123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MODELO_PLANILHA: str = "modelo.xlsx"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()