import importlib.metadata
from typing import Optional

import typer
from typer import Context, Option, Typer, echo

from app.cli.commands import config, import_export, link, version
from app.core.settings import settings

# Initialize Typer for potential future CLI enhancements
cli_app = Typer(
    name=settings.APP_NAME,
    no_args_is_help=True,
    help=f"{settings.APP_NAME} - A powerful bookmark and link management CLI tool",
    epilog="Use 'linkcovery COMMAND --help' for more information about a command.",
)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        try:
            version = importlib.metadata.version("linkcovery")
            echo(f"LinkCovery version {version}")
        except importlib.metadata.PackageNotFoundError:
            echo("LinkCovery version 0.3.1 (development)")
        raise typer.Exit


@cli_app.callback()
def main(
    ctx: Context,
    version_flag: bool | None = Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version information",
    ),
) -> None:
    """LinkCovery - Bookmark and Link Management CLI Tool.

    A powerful CLI tool for managing bookmarks and links with features like:
    - Link storage with metadata
    - Advanced search capabilities
    - Import/Export functionality
    - CLI-based configuration management

    Get started by adding some links!
    """


# Add sub-commands
cli_app.add_typer(link.app, name="link", help="Manage links and bookmarks")
cli_app.add_typer(import_export.app, name="db", help="Import/export data")
cli_app.add_typer(config.app, name="config", help="Manage configuration")
cli_app.add_typer(version.app, name="version", help="Show version information")
