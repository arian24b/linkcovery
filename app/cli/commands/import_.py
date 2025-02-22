from typer import Typer, Option, Exit
from os import path

from app.core.logger import AppLogger
from app.core.utils import check_file
from app.core.database import user_service
from app.core.services.import_export.importer import txt, csv


logger = AppLogger(__name__)

app = Typer()


@app.command("import", help="Import links from a TXT or CSV file.")
def import_links(
    file_path: str = Option(..., help="Path to the .txt or .csv file to import."),
    author_id: int = Option(..., help="ID of the author to associate with the imported links."),
) -> None:
    if not (author := user_service.get_user(user_id=author_id)):
        logger.error(f"Author with ID '{author_id}' does not exist.")
        raise Exit(code=1)

    if check_file(file_path):
        extension = path.splitext(file_path)[1].lower()

    if extension == ".txt":
        txt(file_path, author.id)
    elif extension == ".csv":
        csv(file_path, author.id)
    # elif extension == ".json":
    #     json(file_path, author.id)
    else:
        logger.error(f"Unsupported file extension: {extension}")
