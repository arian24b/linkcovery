"""Data import and export commands for LinkCovery CLI."""

import json
from pathlib import Path

import typer

from linkcovery.cli.cli_state import state
from linkcovery.core.utils import confirm_action, console, err_console, handle_errors


def _data_service():
    from linkcovery.services.data_service import get_data_service

    return get_data_service()


app = typer.Typer(help="Import and export your bookmark data", rich_help_panel="Data Management", no_args_is_help=True)


@app.command()
@handle_errors
def export(
    output: str = typer.Argument("links.json", help="Output file path"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Overwrite without confirmation (same as --force)"),
) -> None:
    """Export all your links to a JSON file.

    Examples:
        linkcovery export my-bookmarks.json
        linkcovery export backup.json --force

    """
    output_path = Path(output)

    overwrite = force or yes
    if output_path.exists() and not overwrite and not confirm_action(f"File {output_path} already exists. Overwrite?"):
        console.print("🛑 Export cancelled", style="yellow")
        return

    data_service = _data_service()
    data_service.export_to_json(output_path)

    if state.json_mode:
        links = data_service.link_service.list_all_links()
        console.print(json.dumps({"exported": len(links), "file": str(output_path)}))


@app.command(name="import")
@handle_errors
def import_data(
    file_path: Path = typer.Argument(..., help="File to import (JSON, HTML or TXT)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip import confirmation"),
) -> None:
    """Import links from a JSON, HTML, or TXT file.

    Examples:
        linkcovery import bookmarks.json
        linkcovery import chrome-bookmarks.html
        linkcovery import links.txt

    """
    if not file_path.exists():
        err_console.print(f"❌ File not found: {file_path}", style="red")
        raise typer.Exit(1)

    if not yes and not confirm_action(f"Import links from {file_path}?"):
        console.print("🛑 Import cancelled", style="yellow")
        return

    data_service = _data_service()

    if file_path.name.endswith(".json"):
        data_service.import_from_json(file_path)
    elif file_path.name.endswith(".html"):
        data_service.import_from_html(file_path)
    elif file_path.name.endswith(".txt"):
        data_service.import_from_txt(file_path)
    else:
        err_console.print(f"❌ Unsupported file format: {file_path}", style="red")
        err_console.print("💡 Hint: supported formats are .json, .html, .txt", style="yellow")
        raise typer.Exit(1)
