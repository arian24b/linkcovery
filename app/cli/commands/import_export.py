from typer import Typer, Option, Exit
from os import path
from pathlib import Path

from app.core.logger import AppLogger
from app.core.utils import check_file
from app.core.database import user_service
from app.core.services.import_export.importer import txt_import, csv_import, json_import
from app.core.services.import_export.exporter import (
    export_users_to_json,
    export_users_to_csv,
    export_links_to_json,
    export_links_to_csv,
)

logger = AppLogger(__name__)
app = Typer()


@app.command("import", help="Import links from a TXT, CSV, or JSON file.")
def import_links(
    file_path: str = Option(..., help="Path to the file to import."),
    author_id: int = Option(..., help="ID of the author to associate with the imported links."),
) -> None:
    if not (author := user_service.get_user(user_id=author_id)):
        logger.error(f"Author with ID '{author_id}' does not exist.")
        raise Exit(code=1)

    try:
        check_file(file_path)
    except Exception as e:
        logger.error(f"Error checking file: {e}")
        return
    extension = path.splitext(file_path)[1].lower()

    if extension == ".txt":
        txt_import(file_path, author.id)
    elif extension == ".csv":
        csv_import(file_path, author.id)
    elif extension == ".json":
        json_import(file_path, author.id)
    else:
        logger.error(f"Unsupported file extension: {extension}")


@app.command("export-users", help="Export all users to a JSON or CSV file.")
def export_users(
    format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
    output: str = Option("users_export.json", "--output", "-o", help="Output file path", show_default=True),
) -> None:
    format = format.lower()
    try:
        if format == "json":
            export_users_to_json(output)
        elif format == "csv":
            export_users_to_csv(output)
        else:
            logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
            raise Exit(code=1)
    except Exception as e:
        logger.error(f"Error exporting users: {e}")
        raise Exit(code=1)


@app.command("export-links", help="Export links to a JSON or CSV file. Optionally filter by author ID.")
def export_links(
    format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
    output: str = Option("links_export.json", "--output", "-o", help="Output file path", show_default=True),
    author_id: int | None = Option(
        None, "--author-id", "-a", help="Filter links by author ID. If not provided, exports all links."
    ),
) -> None:
    format = format.lower()
    try:
        if format == "json":
            export_links_to_json(output, author_id)
        elif format == "csv":
            export_links_to_csv(output, author_id)
        else:
            logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
            raise Exit(code=1)
    except Exception as e:
        logger.error(f"Error exporting links: {e}")
        raise Exit(code=1)


@app.command("export-all", help="Export all users and links to JSON or CSV files.")
def export_all_command(
    format: str = Option(
        "json", "--format", "-f", help="Export format for both users and links: json or csv", show_default=True
    ),
    output_dir: str | None = Option(None, "--output-dir", "-d", help="Directory to store exported files."),
    author_id: int | None = Option(
        None, "--author-id", "-a", help="Filter links by author ID for export. If not provided, exports all links."
    ),
) -> None:
    format = format.lower()
    if format not in {"json", "csv"}:
        logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
        raise Exit(code=1)

    if not output_dir:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory '{output_dir}': {e}")
            raise Exit(code=1)

    users_output = output_dir / f"users_export.{format}"
    links_output = output_dir / f"links_export.{format}"

    try:
        export_users_to_json(str(users_output))
        export_links_to_json(str(links_output), author_id)
        logger.info(f"Exported all data successfully to '{users_output}' and '{links_output}'.")
    except Exception as e:
        logger.error(f"Error exporting all data: {e}")
        raise Exit(code=1)
