"""Modern CLI application for LinkCovery."""

import typer
from rich.table import Table
from datetime import datetime
from pathlib import Path


from linkcovery.cli import config, data, links
from linkcovery.core.config import get_config
from linkcovery.core.utils import console, handle_errors
from linkcovery.services.link_service import get_link_service

# Main app
cli_app = typer.Typer(
    name="linkcovery",
    help="🔗 Modern bookmark and link management tool",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Add command groups
cli_app.add_typer(links.app)
cli_app.add_typer(data.app)
cli_app.add_typer(config.app, name="config")


@cli_app.command(rich_help_panel="Other")
@handle_errors
def stats() -> None:
    """Show bookmark statistics."""
    link_service = get_link_service()
    stats_data = link_service.get_statistics()

    console.print("📊 [bold blue]LinkCovery Statistics[/bold blue]")
    console.print(f"   Total links: [bold]{stats_data['total_links']}[/bold]")
    console.print(f"   Read: [green]{stats_data['read_links']}[/green]")
    console.print(f"   Unread: [yellow]{stats_data['unread_links']}[/yellow]")

    if stats_data["top_domains"]:
        console.print("\n   Top domains:")
        for domain, count in stats_data["top_domains"][:5]:
            console.print(f"     [cyan]{domain}[/cyan]: {count}")


@cli_app.command(rich_help_panel="Other")
@handle_errors
def paths() -> None:
    """Show all LinkCovery file paths."""
    config = get_config()

    table = Table(title="📂 LinkCovery Paths")
    table.add_column("Location", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Modified", style="dim")

    config_file = config.get_config_dir() / "config.json"
    if config_file.exists():
        config_size = f"{config_file.stat().st_size:,} bytes"
        config_modified = datetime.fromtimestamp(config_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    else:
        config_size = "N/A"
        config_modified = "N/A"

    db_path = Path(config.get_database_path())
    if db_path.exists():
        db_size = f"{db_path.stat().st_size:,} bytes"
        db_modified = datetime.fromtimestamp(db_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    else:
        db_size = "N/A"
        db_modified = "N/A"

    data_dir = db_path.parent
    table.add_row("Configuration", str(config_file), config_size, config_modified)
    table.add_row("Database", str(db_path), db_size, db_modified)
    table.add_row("Data Directory", str(data_dir), "-", "-")

    console.print(table)


@cli_app.command(rich_help_panel="Other")
def version() -> None:
    """Show version information."""
    config = get_config()
    console.print(f"🔗 [bold blue]{config.app_name}[/bold blue] v{config.version}")
    console.print("   Modern bookmark and link management tool")


@cli_app.callback(no_args_is_help=True)
def main() -> None:
    """LinkCovery - Modern bookmark management tool.

    Efficiently manage, search, and organize your bookmarks with a clean CLI interface.
    """
    return
