"""Import/Export CLI commands."""

from os import path
from pathlib import Path

from typer import Exit, Option, Typer

from linkcovery.core.logger import Logger
from linkcovery.core.utils import (
    check_file,
    csv_import,
    export_links_to_csv,
    export_links_to_json,
    json_import,
    txt_import,
)

app = Typer(no_args_is_help=True)
logger = Logger(__name__)


@app.command(name="import", help="Import links from a TXT, CSV, or JSON file.")
def import_links(
    file_path: str = Option(..., help="Path to the file to import."),
) -> None:
    try:
        check_file(file_path)
    except Exception as e:
        logger.exception(f"Error checking file: {e}")
        return
    extension = path.splitext(file_path)[1].lower()

    if extension == ".txt":
        txt_import(file_path)
    elif extension == ".csv":
        csv_import(file_path)
    elif extension == ".json":
        json_import(file_path)
    else:
        logger.error(f"Unsupported file extension: {extension}")


@app.command(name="export", help="Export links to a JSON or CSV file.")
def export_links(
    format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
    output: str = Option("links_export.json", "--output", "-o", help="Output file path", show_default=True),
) -> None:
    format = format.lower()
    try:
        if format == "json":
            export_links_to_json(output)
        elif format == "csv":
            export_links_to_csv(output)
        else:
            logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
            raise Exit(code=1)
    except Exception as e:
        logger.exception(f"Error exporting links: {e}")
        raise Exit(code=1)


@app.command(name="backup", help="Export all links to JSON or CSV files.")
def export_all_command(
    format: str = Option(
        "json",
        "--format",
        "-f",
        help="Export format: json or csv",
        show_default=True,
    ),
    output_dir: str | None = Option(None, "--output-dir", "-d", help="Directory to store exported files."),
) -> None:
    format = format.lower()
    if format not in {"json", "csv"}:
        logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
        raise Exit(code=1)

    if not output_dir:
        output_dir_path = Path.cwd()
    else:
        output_dir_path = Path(output_dir)
        try:
            output_dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.exception(f"Failed to create directory '{output_dir_path}': {e}")
            raise Exit(code=1)

    links_output = output_dir_path / f"links_export.{format}"

    try:
        if format == "json":
            export_links_to_json(str(links_output))
        else:  # csv
            export_links_to_csv(str(links_output))
        logger.info(f"Exported all links successfully to '{links_output}'.")
    except Exception as e:
        logger.exception(f"Error exporting links: {e}")
        raise Exit(code=1)
