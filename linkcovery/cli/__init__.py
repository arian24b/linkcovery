"""Modern CLI application for LinKCovery."""

import typer
from rich.console import Console

from linkcovery.cli import config, data, links
from linkcovery.cli.utils import handle_errors
from linkcovery.core.config import get_config
from linkcovery.services.link_service import get_link_service

console = Console()

# Main app
cli_app = typer.Typer(
    name="linkcovery",
    help="🔗 Modern bookmark and link management tool",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Add command groups
cli_app.add_typer(links.app, name="links")
cli_app.add_typer(config.app, name="config")
cli_app.add_typer(data.app, name="data")


@cli_app.command()
@handle_errors
def stats() -> None:
    """Show bookmark statistics."""
    link_service = get_link_service()
    stats = link_service.get_statistics()

    console.print("📊 [bold blue]LinKCovery Statistics[/bold blue]")
    console.print(f"   Total links: [bold]{stats['total_links']}[/bold]")
    console.print(f"   Read: [green]{stats['read_links']}[/green]")
    console.print(f"   Unread: [yellow]{stats['unread_links']}[/yellow]")

    if stats["top_domains"]:
        console.print("\n   Top domains:")
        for domain, count in stats["top_domains"][:5]:
            console.print(f"     [cyan]{domain}[/cyan]: {count}")


@cli_app.command()
def version() -> None:
    """Show version information."""
    config = get_config()
    console.print(f"🔗 [bold blue]{config.app_name}[/bold blue] v{config.version}")
    console.print("   Modern bookmark and link management tool")


@cli_app.callback()
def main() -> None:
    """LinKCovery - Modern bookmark management tool.

    Efficiently manage, search, and organize your bookmarks with a clean CLI interface.
    """
    return
