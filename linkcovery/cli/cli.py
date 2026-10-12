"""Modern CLI application for LinkCovery."""

import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from socket import socket

from cfui import Arg, ui

# importing these registers their commands on the app
from linkcovery.cli import config as _config  # noqa: F401
from linkcovery.cli import data as _data  # noqa: F401
from linkcovery.cli import links as _links  # noqa: F401
from linkcovery.cli.app import app as cli
from linkcovery.cli.app import command
from linkcovery.cli.cli_state import state
from linkcovery.core.utils import handle_errors, print_json


def _get_config():
    from linkcovery.core.config import get_config

    return get_config()


def get_link_service():
    """Lazy proxy: --help must not pay the pydantic/db import cost."""
    from linkcovery.services.link_service import get_link_service as _get

    return _get()


@command(
    cli,
    "webui",
    "Run the LinkCovery web UI",
    args=[
        Arg("--host", default="127.0.0.1", help="Host to bind"),
        Arg("--port", type=int, default=8000, help="Port to listen on"),
        Arg("--reload", action="store_true", help="Auto-reload on code changes"),
        Arg("--background", action="store_true", help="Run web UI in background"),
    ],
)
@handle_errors
def webui(host, port, reload, background) -> None:
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
            ui.error(f"Web UI failed to start at {url} within 10s")
            ui.hint(f"check {log_file} for details")
            raise SystemExit(1)

        ui.success(f"Web UI running at {url}")
        ui.hint(f"Logs: {log_file}")
        ui.hint(f"PID: {process.pid}")
        webbrowser.open(url)
        return

    ui.success(f"Web UI running at {url}")
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


@command(cli, "stats", "Show bookmark statistics")
@handle_errors
def stats() -> None:
    """Show bookmark statistics."""
    link_service = get_link_service()
    stats_data = link_service.get_statistics()

    if state.json_mode:
        print_json(stats_data, ensure_ascii=False, default=str)
        return

    ui.heading("LinkCovery Statistics")
    ui.out(f"   Total links: {stats_data['total_links']}")
    ui.out(f"   Read: {stats_data['read_links']}")
    ui.out(f"   Unread: {stats_data['unread_links']}")

    if stats_data["top_domains"]:
        ui.out("\n   Top domains:")
        for domain, count in stats_data["top_domains"][:5]:
            ui.out(f"     {domain}: {count}")


@command(cli, "paths", "Show all LinkCovery file paths")
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
        print_json(
            {
                "config_file": str(config_file),
                "database": str(db_path),
                "data_dir": str(data_dir),
            }
        )
        return

    ui.table(
        [
            ("Configuration", config_file, config_size, config_modified),
            ("Database", db_path, db_size, db_modified),
            ("Data Directory", data_dir, "-", "-"),
        ],
        ["Location", "Path", "Size", "Modified"],
    )


@command(
    cli,
    "mark",
    "Mark links as read or unread (toggles when neither flag is given)",
    args=[
        Arg("link_ids", type=int, nargs="+", required=True, prompt="Link IDs to mark", help="Link IDs to mark"),
        Arg("-r", "--read", action="store_true", help="Mark as read"),
        Arg("-u", "--unread", action="store_true", help="Mark as unread"),
    ],
)
@handle_errors
def mark(link_ids, read, unread) -> None:
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
                ui.success(f"Marked link #{link_id} as {'read' if new_status else 'unread'}")

        except Exception as e:
            failed = True
            ui.error(f"Failed to mark link #{link_id}: {e}")

    if state.json_mode:
        print_json({"marked": marked, "failed": failed})
    if failed:
        raise SystemExit(1)


@command(
    cli,
    "open",
    "Open links in your default web browser",
    args=[Arg("link_ids", type=int, nargs="+", required=True, prompt="Link IDs to open", help="Link IDs to open")],
)
@handle_errors
def open_link(link_ids) -> None:
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
                ui.info(f"Opening link #{link_id}: {link.url}")
        except Exception as e:
            failed = True
            ui.error(f"Failed to open link #{link_id}: {e}")

    if state.json_mode:
        print_json({"opened": opened, "failed": failed})
    if failed:
        raise SystemExit(1)


def main() -> None:
    cli.main()
