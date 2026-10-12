"""Data import and export commands for LinkCovery CLI."""

from pathlib import Path

from cfui import Arg, ui

from linkcovery.cli.app import app as cli
from linkcovery.cli.app import command
from linkcovery.cli.cli_state import state
from linkcovery.core.utils import confirm_action, handle_errors


def _data_service():
    from linkcovery.services.data_service import get_data_service

    return get_data_service()


@command(
    cli,
    "export",
    "Export all your links (format picked from the suffix: .json, .md, .html)",
    args=[
        Arg("output", nargs="?", default="links.json", help="Output file"),
        Arg("-f", "--force", action="store_true", help="Overwrite existing file"),
        Arg("-y", "--yes", action="store_true", help="Overwrite without confirmation (same as --force)"),
    ],
)
@handle_errors
def export(output, force, yes) -> None:
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
        ui.warning("Export cancelled")
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
        ui.error(f"Unsupported export format: {suffix}")
        ui.hint("use .json, .md, or .html")
        raise SystemExit(1)

    if state.json_mode:
        from linkcovery.core.utils import print_json

        links = data_service.link_service.list_all_links()
        print_json({"exported": len(links), "file": str(output_path), "format": suffix or ".json"})


@command(
    cli,
    "import",
    "Import links from a JSON, HTML, or TXT file (or Chrome)",
    args=[
        Arg("file_path", nargs="?", type=Path, help="File to import (.json/.html/.txt). Omit with --chrome"),
        Arg("--chrome", action="store_true", help="Import from Chrome's bookmarks file"),
        Arg("-y", "--yes", action="store_true", help="Skip import confirmation"),
    ],
)
@handle_errors
def import_data(file_path, chrome, yes) -> None:
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
        ui.error("No file given")
        ui.hint("linkcovery import <file> | linkcovery import --chrome")
        raise SystemExit(1)
    if not file_path.exists():
        ui.error(f"File not found: {file_path}")
        raise SystemExit(1)

    if not yes and not confirm_action(f"Import links from {file_path}?"):
        ui.warning("Import cancelled")
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
        ui.error(f"Unsupported file format: {file_path}")
        ui.hint("supported formats are .json, .html, .txt")
        raise SystemExit(1)
