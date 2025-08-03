from os import path

from app.core.config import config_manager


def check_file(file_path: str) -> bool:
    if not path.exists(file_path):
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)

    extension = path.splitext(file_path)[1].lower()
    allowed_extensions = config_manager.config.allowed_extensions
    if extension not in allowed_extensions:
        msg = f"Invalid file extension: {extension}. Allowed extensions: {allowed_extensions}"
        raise ValueError(msg)

    return True


def get_description(text: str | None) -> str:
    return text or ""
