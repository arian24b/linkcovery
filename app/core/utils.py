from os import path

from app.core.settings import settings


def check_file(file_path: str) -> bool:
    if not path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if (extension := path.splitext(file_path)[1].lower()) not in settings.ALLOW_EXTENSIONS:
        raise ValueError(f"Invalid file extension: {extension}. Allowed extensions: {settings.ALLOW_EXTENSIONS}")

    return True


def get_description(text: str | None) -> str:
    return text
