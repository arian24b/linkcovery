from rich import pretty, traceback
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "LinkCovery"
    DATABASE_NAME: str = "app.db"
    DEBUG: bool = False
    ALLOW_EXTENSIONS: list = [
        ".txt",
        ".csv",
        ".json",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


if settings.DEBUG:
    traceback.install(show_locals=True)
    pretty.install()
