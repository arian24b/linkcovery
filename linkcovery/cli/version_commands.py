"""Version CLI commands."""

import importlib.metadata

from typer import Typer

from linkcovery.core.logger import Logger

app = Typer(no_args_is_help=True)
logger = Logger(__name__)


@app.command(name="show", help="Show version information")
def show_version() -> None:
    """Show the current version of LinkCovery."""
    try:
        # Try to get version from installed package first
        version = importlib.metadata.version("linkcovery")
        logger.print(f"[bold cyan]LinkCovery[/bold cyan] version [bold green]{version}[/bold green]")
    except importlib.metadata.PackageNotFoundError:
        try:
            # Fallback to package version
            import linkcovery

            version = linkcovery.__version__
            logger.print(
                f"[bold cyan]LinkCovery[/bold cyan] version [bold green]{version}[/bold green] "
                f"[yellow](development)[/yellow]",
            )
        except (ImportError, AttributeError):
            logger.print("[yellow]Version information not available (development mode)[/yellow]")


@app.callback(invoke_without_command=True)
def version_callback() -> None:
    """Default callback that shows version when no subcommand is provided."""
    show_version()
