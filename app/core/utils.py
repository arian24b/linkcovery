from os import path

from app.core.settings import settings


def check_file(file_path: str) -> bool:
    if not path.exists(file_path):
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)

    if (extension := path.splitext(file_path)[1].lower()) not in settings.ALLOW_EXTENSIONS:
        msg = f"Invalid file extension: {extension}. Allowed extensions: {settings.ALLOW_EXTENSIONS}"
        raise ValueError(msg)

    return True


def get_description(text: str | None) -> str:
    return text
