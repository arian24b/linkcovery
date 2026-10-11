"""Configuration management commands for LinkCovery CLI."""

import platform
import subprocess
from pathlib import Path

from cfui import Arg, ui

from linkcovery.cli.app import app, command
from linkcovery.cli.cli_state import state
from linkcovery.core.utils import confirm_action, handle_errors, print_json

cli = app.group("config", "Manage LinkCovery configuration")


def _config_manager():
    from linkcovery.core.config import get_config_manager

    return get_config_manager()


def _config():
    from linkcovery.core.config import get_config

    return get_config()


@command(cli, "show", "Show current configuration with each value's source")
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
        print_json(payload)
        return

    rows = []
    for key, value in config_data.items():
        display_value = ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)
        rows.append((key, display_value, config_manager.value_source(key)))
    ui.table(rows, ["Setting", "Value", "Source"])


@command(
    cli,
    "get",
    "Get a specific configuration value",
    args=[Arg("key", required=True, prompt="Configuration key", help="Configuration key to retrieve")],
)
@handle_errors
def get(key) -> None:
    """Get a specific configuration value.

    Examples:
        linkcovery config get max_search_results

    """
    config_manager = _config_manager()
    value = config_manager.get(key)

    ui.out(f"{value}")


@command(
    cli,
    "set",
    "Set a configuration value (run without arguments to list keys)",
    args=[Arg("key", nargs="?", help="Configuration key to set"), Arg("value", nargs="?", help="New value")],
)
@handle_errors
def set(key, value) -> None:
    """Set a configuration value.

    Run without arguments to see all available keys.

    Examples:
        linkcovery config set max_search_results 100
        linkcovery config set debug true
        linkcovery config set

    """
    # If no key provided, show all available keys
    if not key:
        ui.heading("Available Configuration Keys:")
        ui.out()
        ui.out("  app_name           Application name")
        ui.out("  debug              Enable debug mode (true/false)")
        ui.out("  max_search_results  Maximum search results (number)")
        ui.out("  default_export_format Export format (json)")
        ui.out("  allowed_extensions  Allowed file extensions")
        ui.out()
        ui.out("Examples:")
        ui.out("  linkcovery config set debug true")
        ui.out("  linkcovery config set max_search_results 100")
        return

    value = ui.need(value, "value", f"New value for {key}", positional=True)

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
    ui.success(f"Set {key} = {parsed_value}")


@command(
    cli,
    "reset",
    "Reset configuration to defaults",
    args=[Arg("-y", "--yes", action="store_true", help="Skip confirmation")],
)
@handle_errors
def reset(yes) -> None:
    """Reset configuration to defaults.

    Examples:
        linkcovery config reset

    """
    if not yes and not confirm_action("Reset all configuration to defaults?"):
        ui.warning("Reset cancelled")
        return

    config_manager = _config_manager()
    config_manager.reset()
    ui.success("Configuration reset to defaults")


@command(cli, "edit", "Open config file in default editor")
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

        ui.success(f"Opening config file: {config_file}")
    except Exception as e:
        ui.error(f"Failed to open config file: {e}")


@command(cli, "validate", "Validate current configuration values")
@handle_errors
def validate() -> None:
    """Validate current configuration values.

    Examples:
        linkcovery config validate

    """
    _config_manager()

    ui.success("Configuration is valid!")
    db_path = Path(_config().get_database_path())
    config_dir = _config().get_config_dir()
    ui.table(
        [
            ("Database Path", db_path, "ok" if db_path.exists() else "will be created"),
            ("Config Directory", config_dir, "ok" if config_dir.exists() else "will be created"),
        ],
        ["Setting", "Value", "Status"],
    )
