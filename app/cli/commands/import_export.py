from typer import Typer, Option, Exit, prompt
from os import path
from pathlib import Path
from json import load

from app.core.logger import AppLogger
from app.core.models import db
from app.core.services.import_export.importer import (
    check_file,
    import_txt,
    import_csv,
    import_links_from_json,
)
from app.core.services.import_export.exporter import (
    export_users_to_json,
    export_users_to_csv,
    export_links_to_json,
    export_links_to_csv,
    export_all,
)


logger = AppLogger(__name__)

app = Typer()


@app.command("import", help="Import links from a TXT or CSV file.")
def import_links(
    file_path: str = Option(..., help="Path to the .txt or .csv file to import."),
    author_id: int = Option(..., help="ID of the author to associate with the imported links."),
) -> None:
    """
    Import links from a TXT or CSV file into the database.
    """
    try:
        if check_file(file_path):
            extension = path.splitext(file_path)[1].lower()
            try:
                if extension == ".txt":
                    import_txt(file_path, author_id, db)
                elif extension == ".csv":
                    import_csv(file_path, author_id, db)
                elif extension == ".json":
                    with open(file_path, "r", encoding="utf-8") as json_file:
                        data = load(json_file)
                        if isinstance(data, list) and all("url" in item for item in data):
                            import_links_from_json(file_path, db)
                else:
                    logger.error(f"Unsupported file extension: {extension}")
            except Exception as e:
                logger.error(f"Import failed: {e}")
    except FileNotFoundError as fnf_error:
        logger.error(f"{fnf_error}")
        raise Exit(code=1)
    except ValueError as val_error:
        logger.error(f"{val_error}")
        raise Exit(code=1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise Exit(code=1)


@app.command("export-users", help="Export all users to a JSON or CSV file.")
def export_users(
    format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
    output: str = Option("users_export.json", "--output", "-o", help="Output file path", show_default=True),
) -> None:
    """
    Export all users to the specified format (JSON or CSV).
    """
    format = format.lower()
    if format == "json":
        export_users_to_json(db, output)
    elif format == "csv":
        export_users_to_csv(db, output)
    else:
        logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")


@app.command("export-links", help="Export all links to a JSON or CSV file.")
def export_links(
    format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
    output: str = Option("links_export.json", "--output", "-o", help="Output file path", show_default=True),
) -> None:
    """
    Export all links to the specified format (JSON or CSV).
    """
    format = format.lower()
    if format == "json":
        export_links_to_json(db, output)
    elif format == "csv":
        export_links_to_csv(db, output)
    else:
        logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")


@app.command("export-all", help="Export all users and links to JSON or CSV files.")
def export_all_command(
    format: str = Option(
        "json", "--format", "-f", help="Export format for both users and links: json or csv", show_default=True
    ),
    output_dir: str | None = Option(None, "--output-dir", "-d", help="Directory to store exported files."),
) -> None:
    """
    Export all users and links to the specified format (JSON or CSV) within a directory.
    """
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

    for output_path in [users_output, links_output]:
        if output_path.exists():
            overwrite = prompt(f"File '{output_path}' already exists. Overwrite? (y/n)", default="n")
            if overwrite.lower() != "y":
                logger.warning(f"Skipped exporting to '{output_path}'.")
                raise Exit()

    export_all(db, format, str(output_dir))
