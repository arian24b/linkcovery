import importlib.metadata

import typer
from typer import Context, Option, Typer, echo

from linkcovery.cli import config_commands, import_export_commands, link_commands, version_commands
from linkcovery.core.settings import settings

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
            try:
                import linkcovery

                version = linkcovery.__version__
                echo(f"LinkCovery version {version} (development)")
            except (ImportError, AttributeError):
                echo("LinkCovery version unknown (development)")
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
cli_app.add_typer(link_commands.app, name="link", help="Manage links and bookmarks")
cli_app.add_typer(import_export_commands.app, name="import-export", help="Import/export data")
cli_app.add_typer(config_commands.app, name="config", help="Manage configuration")
cli_app.add_typer(version_commands.app, name="version", help="Show version information")
