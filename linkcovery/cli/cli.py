"""Modern CLI application for LinkCovery."""

import json
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from socket import socket

import typer
from rich.table import Table

from linkcovery import __version__
from linkcovery.cli import config, data, links
from linkcovery.cli.cli_state import state
from linkcovery.core.utils import console, err_console, handle_errors


def _get_config():
    from linkcovery.core.config import get_config

    return get_config()


def get_link_service():
    """Lazy proxy: --help must not pay the pydantic/db import cost."""
    from linkcovery.services.link_service import get_link_service as _get

    return _get()


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


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"linkcovery {__version__}")
        raise typer.Exit(0)


@cli_app.callback(no_args_is_help=True)
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    json_mode: bool = typer.Option(False, "--json", help="Output machine-readable JSON"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
) -> None:
    """LinkCovery - Modern bookmark management tool.

    Efficiently manage, search, and organize your bookmarks with a clean CLI interface.
    """
    state.json_mode = json_mode
    state.no_color = no_color
    if no_color:
        console.no_color = True
        err_console.no_color = True
        import os

        os.environ["NO_COLOR"] = "1"


@cli_app.command(rich_help_panel="Other")
@handle_errors
def webui(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", help="Port to listen on"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on code changes"),
    background: bool = typer.Option(False, "--background", help="Run web UI in background"),
) -> None:
    """Run the LinkCovery web UI."""
    import uvicorn

    from linkcovery.webui.app import app

    url = f"http://{host}:{port}"

    if background:
        log_dir = _get_config().get_log_dir()
        log_file = log_dir / "webui.log"
        command = [sys.executable, "-m", "uvicorn", "linkcovery.webui.app:app", "--host", host, "--port", str(port)]
        if reload:
            command.append("--reload")
        with open(log_file, "ab") as log_handle:
            process = subprocess.Popen(command, stdout=log_handle, stderr=log_handle)

        if not _wait_for_port(host, port, timeout=10.0):
            process.terminate()
            err_console.print(f"❌ Web UI failed to start at {url} within 10s", style="red")
            err_console.print(f"💡 Hint: check {log_file} for details", style="yellow")
            raise typer.Exit(1)

        console.print(f"🌐 Web UI running at {url}", style="green")
        console.print(f"🧾 Logs: {log_file}", style="dim")
        console.print(f"🧩 PID: {process.pid}", style="dim")
        webbrowser.open(url)
        return

    console.print(f"🌐 Web UI running at {url}", style="green")
    webbrowser.open(url)
    if reload:
        uvicorn.run("linkcovery.webui.app:app", host=host, port=port, reload=True)
    else:
        uvicorn.run(app, host=host, port=port)


def _wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool:
    """Poll until the port accepts connections or give up."""
    from time import sleep, time

    deadline = time() + timeout
    while time() < deadline:
        try:
            with socket() as sock:
                sock.settimeout(0.5)
                if sock.connect_ex((host, port)) == 0:
                    return True
        except OSError:
            pass
        sleep(0.2)
    return False


@cli_app.command(rich_help_panel="Other")
@handle_errors
def stats() -> None:
    """Show bookmark statistics."""
    link_service = get_link_service()
    stats_data = link_service.get_statistics()

    if state.json_mode:
        console.print(json.dumps(stats_data, ensure_ascii=False, default=str))
        return

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
    config = _get_config()

    config_file = config.get_config_dir() / "config.json"
    config_size = f"{config_file.stat().st_size:,} bytes" if config_file.exists() else "N/A"
    config_modified = (
        datetime.fromtimestamp(config_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        if config_file.exists()
        else "N/A"
    )

    db_path = Path(config.get_database_path())
    db_size = f"{db_path.stat().st_size:,} bytes" if db_path.exists() else "N/A"
    db_modified = (
        datetime.fromtimestamp(db_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if db_path.exists() else "N/A"
    )

    data_dir = db_path.parent

    if state.json_mode:
        console.print(
            json.dumps(
                {
                    "config_file": str(config_file),
                    "database": str(db_path),
                    "data_dir": str(data_dir),
                }
            )
        )
        return

    table = Table(title="📂 LinkCovery Paths", box=None, header_style="dim")
    table.add_column("Location", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Size", style="yellow", justify="right")
    table.add_column("Modified", style="dim")
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

    failed = False
    marked = []
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
            else:
                link_service.mark_as_unread(link_id)
            marked.append({"id": link_id, "is_read": new_status})
            if not state.json_mode:
                console.print(f"✅ Marked link #{link_id} as {'read' if new_status else 'unread'}", style="green")

        except Exception as e:
            failed = True
            err_console.print(f"❌ Failed to mark link #{link_id}: {e}", style="red")

    if state.json_mode:
        console.print(json.dumps({"marked": marked, "failed": failed}))
    if failed:
        raise typer.Exit(1)


@cli_app.command(rich_help_panel="Link Management")
@handle_errors
def open_link(
    link_ids: list[int] = typer.Argument(..., help="Link IDs to open"),
) -> None:
    """Open links in your default web browser.

    Examples:
        linkcovery open 1              # Open link #1
        linkcovery open 1 2 3          # Open multiple links

    """
    link_service = get_link_service()

    failed = False
    opened = []
    for link_id in link_ids:
        try:
            link = link_service.get_link(link_id)
            link_service.open_link(link_id)
            opened.append({"id": link_id, "url": link.url})
            if not state.json_mode:
                console.print(f"🌐 Opening link #{link_id}: {link.url}", style="blue")
        except Exception as e:
            failed = True
            err_console.print(f"❌ Failed to open link #{link_id}: {e}", style="red")

    if state.json_mode:
        console.print(json.dumps({"opened": opened, "failed": failed}))
    if failed:
        raise typer.Exit(1)


# Command aliases (hidden from main help): same functions, registered under second names.
cli_app.command(name="ls", hidden=True, rich_help_panel="Link Management")(links.list_links)
cli_app.command(name="find", hidden=True, rich_help_panel="Link Management")(links.search)
cli_app.command(name="new", hidden=True, rich_help_panel="Link Management")(links.add)
cli_app.command(name="rm", hidden=True, rich_help_panel="Link Management")(links.delete)
