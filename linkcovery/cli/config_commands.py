"""Configuration management CLI commands."""

import importlib.metadata
import json

from rich.table import Table
from typer import Argument, Typer

from linkcovery.core.logger import Logger
from linkcovery.core.settings import config_manager

app = Typer(no_args_is_help=True)
logger = Logger(__name__)


@app.command(name="get", help="Get a configuration value")
def get_config(
    key: str = Argument(..., help="Configuration key to retrieve"),
) -> None:
    """Get a specific configuration value."""
    value = config_manager.get_setting(key)
    if value is None:
        logger.error(f"Configuration key '{key}' not found.")
        return

    logger.print(f"[bold cyan]{key}[/bold cyan]: {value}")


@app.command(name="set", help="Set a configuration value")
def set_config(
    key: str = Argument(..., help="Configuration key to set"),
    value: str = Argument(..., help="Configuration value to set"),
) -> None:
    """Set a specific configuration value."""
    # Try to parse the value as JSON first for complex types
    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        # If it's not valid JSON, treat it as a string
        parsed_value = value

    # Handle boolean conversion
    if isinstance(parsed_value, str) and parsed_value.lower() in ("true", "false"):
        parsed_value = parsed_value.lower() == "true"

    if config_manager.set_setting(key, parsed_value):
        logger.print(f"[green]Successfully set[/green] [bold cyan]{key}[/bold cyan] = {parsed_value}")
    else:
        logger.error(f"Failed to set configuration key '{key}'. Key may not exist.")


@app.command(name="list", help="List all configuration values")
def list_config() -> None:
    """List all configuration values."""
    config_dict = config_manager.get_config_dict()

    table = Table(title="Configuration")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Type", style="green")

    for key, value in config_dict.items():
        # Format lists nicely
        formatted_value = ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)

        table.add_row(key, formatted_value, type(value).__name__)

    logger.print(table)


@app.command(name="reset", help="Reset configuration to defaults")
def reset_config() -> None:
    """Reset configuration to default values."""
    config_manager.reset_config()
    logger.print("[green]Configuration reset to defaults successfully.[/green]")


@app.command(name="path", help="Show configuration file path")
def show_config_path() -> None:
    """Show the path to the configuration file."""
    config_path = config_manager.get_config_file_path()
    logger.print(f"Configuration file: [bold cyan]{config_path}[/bold cyan]")


@app.command(name="edit", help="Show configuration for manual editing")
def edit_config() -> None:
    """Show current configuration in JSON format for manual editing."""
    config_dict = config_manager.get_config_dict()
    formatted_config = json.dumps(config_dict, indent=2)

    logger.print("[bold]Current configuration:[/bold]")
    logger.print(f"[dim]{formatted_config}[/dim]")
    logger.print(
        f"\n[yellow]To edit manually, modify:[/yellow] [bold cyan]{config_manager.get_config_file_path()}[/bold cyan]",
    )


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
