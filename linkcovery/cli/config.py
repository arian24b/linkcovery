"""Configuration management commands for LinkCovery CLI."""

import os
import platform

import typer
from rich.table import Table as RichTable

from linkcovery.core.config import get_config, get_config_manager
from linkcovery.core.utils import console, handle_errors

app = typer.Typer(help="Manage LinkCovery configuration", rich_help_panel="Configuration", no_args_is_help=True)


@app.command(rich_help_panel="Configuration")
@handle_errors
def show() -> None:
    """Show current configuration.

    Examples:
        linkcovery config show

    """
    config_manager = get_config_manager()
    config_data = config_manager.list_all()

    table = RichTable(title="⚙️ LinkCovery Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in config_data.items():
        # Format the display value
        if isinstance(value, bool):
            display_value = "✅ True" if value else "❌ False"
        elif isinstance(value, list):
            display_value = ", ".join(str(v) for v in value)
        else:
            display_value = str(value)

        table.add_row(key, display_value)

    console.print(table)


@app.command(rich_help_panel="Configuration")
@handle_errors
def get(key: str = typer.Argument(..., help="Configuration key to retrieve")) -> None:
    """Get a specific configuration value.

    Examples:
        linkcovery config get max_search_results

    """
    config_manager = get_config_manager()
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

    config_manager = get_config_manager()

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
def reset() -> None:
    """Reset configuration to defaults.

    Examples:
        linkcovery config reset

    """
    from linkcovery.core.utils import confirm_action

    if not confirm_action("Reset all configuration to defaults?"):
        console.print("🛑 Reset cancelled", style="yellow")
        return

    config_manager = get_config_manager()
    config_manager.reset()
    console.print("✅ Configuration reset to defaults", style="green")


@app.command(rich_help_panel="Configuration")
@handle_errors
def edit() -> None:
    """Open config file in default editor.

    Examples:
        linkcovery config edit

    """
    config_manager = get_config_manager()

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
    from pathlib import Path

    get_config_manager()

    console.print("✅ Configuration is valid!", style="green")
    table = RichTable(title="Configuration Summary")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")

    # Check database path exists and is writable
    db_path = Path(get_config().get_database_path())
    db_status = "✅ OK" if db_path.exists() else "⚠️  Will be created"
    table.add_row("Database Path", str(db_path), db_status)

    # Check config dir exists
    config_dir = get_config().get_config_dir()
    config_status = "✅ OK" if config_dir.exists() else "⚠️  Will be created"
    table.add_row("Config Directory", str(config_dir), config_status)

    console.print(table)
