"""Simple main CLI app for LinKCovery."""

import typer
from rich import print

from linkcovery.cli.commands import app as commands_app
from linkcovery.core.config import config


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        print(f"{config.APP_NAME} v{config.VERSION}")
        raise typer.Exit


# Main app
cli_app = typer.Typer(name="linkcovery", help="Simple bookmark and link management", no_args_is_help=True)


# Add version option
@cli_app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version",
    ),
) -> None:
    """LinKCovery - Simple bookmark management."""
    return


# Add all commands
cli_app.add_typer(commands_app, name="")
