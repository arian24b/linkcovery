# src/settings.py

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    DATABASE_NAME: str = Field("app.db", env="DATABASE_NAME")
    DEBUG: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
