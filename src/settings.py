from rich import pretty, traceback
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    traceback.install(show_locals=True)
    pretty.install()

    DATABASE_NAME: str = "app.db"
    DEBUG: bool = False
    ALLOW_EXTENSIONS: list = ["csv", "txt"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
