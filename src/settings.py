from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_NAME: str = "app.db"

    class Config:
        env_file = ".env"


settings = Settings()
