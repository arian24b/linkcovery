"""Modern CLI application for LinkCovery."""

from datetime import datetime
from pathlib import Path

import typer
from rich.table import Table

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


@cli_app.command(rich_help_panel="Link Management")
@handle_errors
def mark(
    link_ids: list[int] = typer.Argument(..., help="Link IDs to mark"),
    read: bool = typer.Option(None, "--read", "-r", help="Mark as read"),
    unread: bool = typer.Option(None, "--unread", "-u", help="Mark as unread"),
) -> None:
    """Mark links as read or unread.

    If neither --read nor --unread is specified, toggles the current status.

    Examples:
        linkcovery mark 1              # Toggle link #1
        linkcovery mark 1 2 3          # Toggle multiple links
        linkcovery mark 1 --read       # Force link #1 as read
        linkcovery mark 1 2 --unread   # Force links #1-2 as unread

    """
    link_service = get_link_service()

    for link_id in link_ids:
        try:
            link = link_service.get_link(link_id)

            if read is True:
                new_status = True
            elif unread is True:
                new_status = False
            else:
                new_status = not link.is_read

            if new_status:
                link_service.mark_as_read(link_id)
                console.print(f"✅ Marked link #{link_id} as read", style="green")
            else:
                link_service.mark_as_unread(link_id)
                console.print(f"✅ Marked link #{link_id} as unread", style="green")

        except Exception as e:
            console.print(f"❌ Failed to mark link #{link_id}: {e}", style="red")


@cli_app.command(rich_help_panel="Link Management")
@handle_errors
def open_link(
    link_ids: list[int] = typer.Argument(..., help="Link IDs to open"),
) -> None:
    """Open links in your default web browser.

    Examples:
        linkcovery open 1              # Open link #1
        linkcovery open 1 2 3         # Open multiple links

    """
    link_service = get_link_service()

    for link_id in link_ids:
        try:
            link = link_service.get_link(link_id)
            link_service.open_link(link_id)
            console.print(f"🌐 Opening link #{link_id}: {link.url}", style="blue")
        except Exception as e:
            console.print(f"❌ Failed to open link #{link_id}: {e}", style="red")


# Command aliases (hidden from main help)
@cli_app.command(rich_help_panel="Link Management", hidden=True)
@handle_errors
def ls(*args, **kwargs) -> None:
    """Alias for 'list' command."""
    from linkcovery.cli.links import list_links

    list_links(*args, **kwargs)


@cli_app.command(rich_help_panel="Link Management", hidden=True)
@handle_errors
def find(*args, **kwargs) -> None:
    """Alias for 'search' command."""
    from linkcovery.cli.links import search

    search(*args, **kwargs)


@cli_app.command(rich_help_panel="Link Management", hidden=True)
@handle_errors
def new(*args, **kwargs) -> None:
    """Alias for 'add' command."""
    from linkcovery.cli.links import add

    add(*args, **kwargs)


@cli_app.command(rich_help_panel="Link Management", hidden=True)
@handle_errors
def rm(*args, **kwargs) -> None:
    """Alias for 'delete' command."""
    from linkcovery.cli.links import delete

    delete(*args, **kwargs)


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
