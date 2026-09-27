"""Data import and export commands for LinkCovery CLI."""

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
    output: str = typer.Argument("links.json", help="Output file (.json/.md/.html, suffix picks format)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Overwrite without confirmation (same as --force)"),
) -> None:
    """Export all your links.

    Format is picked from the output suffix: .json, .md, .html.

    Examples:
        linkcovery export my-bookmarks.json
        linkcovery export my-bookmarks.md
        linkcovery export my-bookmarks.html --force

    """
    output_path = Path(output)

    overwrite = force or yes
    if output_path.exists() and not overwrite and not confirm_action(f"File {output_path} already exists. Overwrite?"):
        console.print("🛑 Export cancelled", style="yellow")
        return

    data_service = _data_service()
    suffix = output_path.suffix.lower()
    if suffix == ".md":
        data_service.export_to_markdown(output_path)
    elif suffix == ".html":
        data_service.export_to_html(output_path)
    elif suffix == ".json" or not suffix:
        data_service.export_to_json(output_path)
    else:
        err_console.print(f"❌ Unsupported export format: {suffix}", style="red")
        err_console.print("💡 Hint: use .json, .md, or .html", style="yellow")
        raise typer.Exit(1)

    if state.json_mode:
        from linkcovery.core.utils import print_json

        links = data_service.link_service.list_all_links()
        print_json({"exported": len(links), "file": str(output_path), "format": suffix or ".json"})


@app.command(name="import")
@handle_errors
def import_data(
    file_path: Path | None = typer.Argument(None, help="File to import (.json/.html/.txt). Omit with --chrome."),
    chrome: bool = typer.Option(False, "--chrome", help="Import from Chrome's bookmarks file"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip import confirmation"),
) -> None:
    """Import links from a JSON, HTML, or TXT file (or Chrome).

    Examples:
        linkcovery import bookmarks.json
        linkcovery import chrome-bookmarks.html
        linkcovery import links.txt
        linkcovery import --chrome

    """
    from linkcovery.core.chrome_bookmark import default_chrome_bookmarks

    if chrome:
        file_path = file_path or default_chrome_bookmarks()
    if file_path is None:
        err_console.print("❌ No file given", style="red")
        err_console.print("💡 Hint: linkcovery import <file> | linkcovery import --chrome", style="yellow")
        raise typer.Exit(1)
    if not file_path.exists():
        err_console.print(f"❌ File not found: {file_path}", style="red")
        raise typer.Exit(1)

    if not yes and not confirm_action(f"Import links from {file_path}?"):
        console.print("🛑 Import cancelled", style="yellow")
        return

    data_service = _data_service()

    suffix = file_path.suffix.lower()
    if suffix == ".json":
        data_service.import_from_json(file_path)
    elif suffix in {".html", ".htm"} or file_path.name == "Bookmarks":
        # HTML export or Chrome's raw Bookmarks JSON — sorted out inside
        data_service.import_from_html(file_path)
    elif suffix == ".txt":
        data_service.import_from_txt(file_path)
    else:
        err_console.print(f"❌ Unsupported file format: {file_path}", style="red")
        err_console.print("💡 Hint: supported formats are .json, .html, .txt", style="yellow")
        raise typer.Exit(1)
