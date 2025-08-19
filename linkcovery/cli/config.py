"""Configuration management commands for LinKCovery CLI."""

import typer
from rich.table import Table

from linkcovery.core.config import get_config_manager
from linkcovery.core.utils import console, handle_errors

app = typer.Typer(help="Manage LinKCovery configuration", no_args_is_help=True)


@app.command()
@handle_errors
def show() -> None:
    """Show current configuration."""
    config_manager = get_config_manager()
    config_data = config_manager.list_all()

    table = Table(title="⚙️ LinKCovery Configuration")
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


@app.command()
@handle_errors
def get(key: str = typer.Argument(..., help="Configuration key to retrieve")) -> None:
    """Get a specific configuration value."""
    config_manager = get_config_manager()
    value = config_manager.get(key)

    console.print(f"⚙️ {key}: {value}")


@app.command()
@handle_errors
def set(
    key: str = typer.Argument(..., help="Configuration key to set"),
    value: str = typer.Argument(..., help="New value for the configuration key"),
) -> None:
    """Set a configuration value."""
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


@app.command()
@handle_errors
def reset() -> None:
    """Reset configuration to defaults."""
    from linkcovery.core.utils import confirm_action

    if not confirm_action("Reset all configuration to defaults?"):
        console.print("🛑 Reset cancelled", style="yellow")
        return

    config_manager = get_config_manager()
    config_manager.reset()
    console.print("✅ Configuration reset to defaults", style="green")
