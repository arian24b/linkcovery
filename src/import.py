from os import path
from rich import print

from settings import settings
from database import Link


def check_file(file_path: str) -> bool:
    if not path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if (extension := file_path.split(".")[-1]) not in settings.ALLOW_EXTENTIONS:
        raise ValueError(f"Invalid file extension: {extension}, allowed extensions: {settings.ALLOW_EXTENTIONS}")

    return True


def import_txt(file_path: str) -> iter[str]:
    with open(file_path, "r", encoding="utf-8") as txtfile:
        for line in txtfile:
            yield line.rstrip()
