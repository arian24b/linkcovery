"""Data import and export commands for LinKCovery CLI."""

from pathlib import Path

import typer

from linkcovery.core.utils import confirm_action, console, handle_errors
from linkcovery.services.data_service import get_data_service

app = typer.Typer(help="Import and export your bookmark data", no_args_is_help=True)


@app.command()
@handle_errors
def export(
    output: str = typer.Argument("links.json", help="Output file path"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
) -> None:
    """Export all your links to a JSON file."""
    output_path = Path(output)

    # Check if file exists and ask for confirmation
    if output_path.exists() and not force and not confirm_action(f"File {output_path} already exists. Overwrite?"):
        console.print("🛑 Export cancelled", style="yellow")
        return

    data_service = get_data_service()
    data_service.export_to_json(output_path)


@app.command(name="import")
@handle_errors
def import_data(
    file_path: Path = typer.Argument(..., help="JSON file to import"),
) -> None:
    """Import links from a JSON file."""
    if not file_path.exists():
        console.print(f"❌ File not found: {file_path}", style="red")
        raise typer.Exit(1)

    # Confirm import
    if not confirm_action(f"Import links from {file_path}?"):
        console.print("🛑 Import cancelled", style="yellow")
        return

    data_service = get_data_service()

    if file_path.name.endswith(".json"):
        data_service.import_from_json(file_path)
    elif file_path.name.endswith(".html"):
        data_service.import_from_html(file_path)
    else:
        console.print(f"❌ Unsupported file format: {file_path}", style="red")
        raise typer.Exit(1)
