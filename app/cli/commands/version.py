"""Version command for the CLI."""

import importlib.metadata

from typer import Typer

from app.core.logger import AppLogger

logger = AppLogger(__name__)
app = Typer(name="version", help="Show version information")


@app.command(name="show", help="Show version information")
def show_version() -> None:
    """Show the current version of LinkCovery."""
    try:
        version = importlib.metadata.version("linkcovery")
        logger.print(f"[bold cyan]LinkCovery[/bold cyan] version [bold green]{version}[/bold green]")
    except importlib.metadata.PackageNotFoundError:
        logger.print("[yellow]Version information not available (development mode)[/yellow]")


@app.callback(invoke_without_command=True)
def version_callback() -> None:
    """Default callback that shows version when no subcommand is provided."""
    show_version()
