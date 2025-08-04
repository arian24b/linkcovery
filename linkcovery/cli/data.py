"""Data import and export commands for LinKCovery CLI."""

from pathlib import Path

import typer
from rich.console import Console

from linkcovery.cli.utils import confirm_action, handle_errors
from linkcovery.services.import_export_service import get_import_export_service

console = Console()
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

    import_export_service = get_import_export_service()
    import_export_service.export_to_json(output_path)


@app.command(name="import")
@handle_errors
def import_data(
    input_file: str = typer.Argument(..., help="JSON file to import"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be imported without actually importing"),
) -> None:
    """Import links from a JSON file."""
    input_path = Path(input_file)

    if not input_path.exists():
        console.print(f"❌ File not found: {input_path}", style="red")
        raise typer.Exit(1)

    if dry_run:
        # TODO: Implement dry run functionality
        console.print("🔍 Dry run mode not yet implemented", style="yellow")
        return

    # Confirm import
    if not confirm_action(f"Import links from {input_path}?"):
        console.print("🛑 Import cancelled", style="yellow")
        return

    import_export_service = get_import_export_service()
    import_export_service.import_from_json(input_path)
