"""Configuration management commands for LinkCovery CLI."""

import json
import platform
import subprocess
from pathlib import Path

import typer
from rich.table import Table as RichTable

from linkcovery.cli.cli_state import state
from linkcovery.core.utils import confirm_action, console, handle_errors


def _config_manager():
    from linkcovery.core.config import get_config_manager

    return get_config_manager()


def _config():
    from linkcovery.core.config import get_config

    return get_config()


app = typer.Typer(help="Manage LinkCovery configuration", rich_help_panel="Configuration", no_args_is_help=True)


@app.command(rich_help_panel="Configuration")
@handle_errors
def show() -> None:
    """Show current configuration with each value's source.

    Examples:
        linkcovery config show

    """
    config_manager = _config_manager()
    config_data = config_manager.list_all()

    # database_path resolves specially (env wins); show the effective value.
    if config_manager.value_source("database_path") == "env":
        from os import getenv

        config_data["database_path"] = getenv("LINKCOVERY_DB")

    if state.json_mode:
        payload = {key: {"value": v, "source": config_manager.value_source(key)} for key, v in config_data.items()}
        console.print(json.dumps(payload, ensure_ascii=False, default=str))
        return

    table = RichTable(title="⚙️ LinkCovery Configuration", box=None, header_style="dim")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Source", style="dim")

    for key, value in config_data.items():
        if isinstance(value, bool):
            display_value = "✅ True" if value else "❌ False"
        elif isinstance(value, list):
            display_value = ", ".join(str(v) for v in value)
        else:
            display_value = str(value)

        table.add_row(key, display_value, config_manager.value_source(key))

    console.print(table)


@app.command(rich_help_panel="Configuration")
@handle_errors
def get(key: str = typer.Argument(..., help="Configuration key to retrieve")) -> None:
    """Get a specific configuration value.

    Examples:
        linkcovery config get max_search_results

    """
    config_manager = _config_manager()
    value = config_manager.get(key)

    console.print(f"⚙️ {key}: {value}")


@app.command(rich_help_panel="Configuration")
@handle_errors
def set(
    key: str = typer.Argument(None, help="Configuration key to set"),
    value: str = typer.Argument(None, help="New value for configuration key"),
) -> None:
    """Set a configuration value.

    Run without arguments to see all available keys.

    Examples:
        linkcovery config set max_search_results 100
        linkcovery config set debug true
        linkcovery config set

    """
    # If no key provided, show all available keys
    if not key:
        console.print("📋 Available Configuration Keys:", style="bold blue")
        console.print()
        console.print("  [cyan]app_name[/cyan]           Application name")
        console.print("  [cyan]debug[/cyan]              Enable debug mode (true/false)")
        console.print("  [cyan]max_search_results[/cyan]  Maximum search results (number)")
        console.print("  [cyan]default_export_format[/cyan] Export format (json)")
        console.print("  [cyan]allowed_extensions[/cyan]  Allowed file extensions")
        console.print()
        console.print("Examples:")
        console.print("  linkcovery config set debug true")
        console.print("  linkcovery config set max_search_results 100")
        return

    if not value:
        console.print("❌ Please provide a value to set", style="red")
        console.print("💡 Usage: linkcovery config set <key> <value>", style="yellow")
        raise typer.Exit(1)

    config_manager = _config_manager()

    # Try to parse the value as the appropriate type
    parsed_value = value

    # Handle boolean values
    if value.lower() in ("true", "yes", "1", "on"):
        parsed_value = True
    elif value.lower() in ("false", "no", "0", "off"):
        parsed_value = False
    # Handle integers
    elif value.isdigit():
        parsed_value = int(value)
    # Handle lists (comma-separated)
    elif "," in value:
        parsed_value = [item.strip() for item in value.split(",")]

    config_manager.set(key, parsed_value)
    console.print(f"✅ Set {key} = {parsed_value}", style="green")


@app.command(rich_help_panel="Configuration")
@handle_errors
def reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Reset configuration to defaults.

    Examples:
        linkcovery config reset

    """
    if not yes and not confirm_action("Reset all configuration to defaults?"):
        console.print("🛑 Reset cancelled", style="yellow")
        return

    config_manager = _config_manager()
    config_manager.reset()
    console.print("✅ Configuration reset to defaults", style="green")


@app.command(rich_help_panel="Configuration")
@handle_errors
def edit() -> None:
    """Open config file in default editor.

    Examples:
        linkcovery config edit

    """
    config_manager = _config_manager()

    try:
        config_file = str(config_manager._config_file)

        if platform.system() == "Windows":
            subprocess.Popen(["cmd", "/c", "start", "", config_file])
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", config_file])
        else:  # Linux
            subprocess.Popen(["xdg-open", config_file])

        console.print(f"📝 Opening config file: {config_file}", style="green")
    except Exception as e:
        console.print(f"❌ Failed to open config file: {e}", style="red")


@app.command(rich_help_panel="Configuration")
@handle_errors
def validate() -> None:
    """Validate current configuration values.

    Examples:
        linkcovery config validate

    """
    _config_manager()

    console.print("✅ Configuration is valid!", style="green")
    table = RichTable(title="Configuration Summary")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")

    # Check database path exists and is writable
    db_path = Path(_config().get_database_path())
    db_status = "✅ OK" if db_path.exists() else "⚠️  Will be created"
    table.add_row("Database Path", str(db_path), db_status)

    # Check config dir exists
    config_dir = _config().get_config_dir()
    config_status = "✅ OK" if config_dir.exists() else "⚠️  Will be created"
    table.add_row("Config Directory", str(config_dir), config_status)

    console.print(table)
