from typer import Typer, Option, Exit
from os import path

from app.core.logger import AppLogger
from app.core.utils import check_file
from app.core.database import user_service
from app.core.services.import_export.importer import txt, csv
# from app.core.services.import_export.exporter import (
#     export_users_to_json,
#     export_users_to_csv,
#     export_links_to_json,
#     export_links_to_csv,
#     export_all,
# )

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


# @app.command("export-users", help="Export all users to a JSON or CSV file.")
# def export_users(
#     format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
#     output: str = Option("users_export.json", "--output", "-o", help="Output file path", show_default=True),
# ) -> None:
#     """
#     Export all users to the specified format (JSON or CSV).
#     """
#     format = format.lower()
#     if format == "json":
#         export_users_to_json(user_service, output)
#     elif format == "csv":
#         export_users_to_csv(user_service, output)
#     else:
#         logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")


# @app.command("export-links", help="Export all links to a JSON or CSV file.")
# def export_links(
#     format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
#     output: str = Option("links_export.json", "--output", "-o", help="Output file path", show_default=True),
# ) -> None:
#     """
#     Export all links to the specified format (JSON or CSV).
#     """
#     format = format.lower()
#     if format == "json":
#         export_links_to_json(link_service, output)
#     elif format == "csv":
#         export_links_to_csv(link_service, output)
#     else:
#         logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")


# @app.command("export-all", help="Export all users and links to JSON or CSV files.")
# def export_all_command(
#     format: str = Option(
#         "json", "--format", "-f", help="Export format for both users and links: json or csv", show_default=True
#     ),
#     output_dir: str | None = Option(None, "--output-dir", "-d", help="Directory to store exported files."),
# ) -> None:
#     """
#     Export all users and links to the specified format (JSON or CSV) within a directory.
#     """
#     format = format.lower()
#     if format not in {"json", "csv"}:
#         logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
#         raise Exit(code=1)

#     if not output_dir:
#         output_dir = Path.cwd()
#     else:
#         output_dir = Path(output_dir)
#         try:
#             output_dir.mkdir(parents=True, exist_ok=True)
#         except Exception as e:
#             logger.error(f"Failed to create directory '{output_dir}': {e}")
#             raise Exit(code=1)

#     users_output = output_dir / f"users_export.{format}"
#     links_output = output_dir / f"links_export.{format}"

#     for output_path in [users_output, links_output]:
#         if output_path.exists():
#             overwrite = prompt(f"File '{output_path}' already exists. Overwrite? (y/n)", default="n")
#             if overwrite.lower() != "y":
#                 logger.warning(f"Skipped exporting to '{output_path}'.")
#                 raise Exit()

#     export_all(user_service, link_service, format, str(output_dir))
