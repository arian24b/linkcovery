from os import path
from rich import print
from pydantic import HttpUrl

from settings import settings
from database import LinkDatabase, Link


def check_file(file_path: str) -> bool:
    if not path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if (extension := file_path.split(".")[-1]) not in settings.ALLOW_EXTENTIONS:
        raise ValueError(f"Invalid file extension: {extension}, allowed extensions: {settings.ALLOW_EXTENTIONS}")

    return True


def import_txt(file_path: str, author_id: int):
    with open(file_path, "r", encoding="utf-8") as txtfile:
        db = LinkDatabase()
        for line in txtfile:
            link = line.rstrip()
            _ = link.split("/")
            link_obj = Link(
                id=None,
                url=HttpUrl(link),
                domain=_[2],
                description="_".join(_[3:]),
                tag=_[2].split("."),
                author_id=author_id,
            )
            db.create_link(link_obj)
