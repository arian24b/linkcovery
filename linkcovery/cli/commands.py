# CLI commands package
"""Configuration management CLI commands."""

import importlib.metadata
import json
from os import path
from pathlib import Path

from rich.table import Table
from typer import Argument, Exit, Option, Typer, prompt

from linkcovery.core.database import link_service
from linkcovery.core.logger import Logger
from linkcovery.core.settings import config_manager
from linkcovery.core.utils import (
    check_file,
    csv_import,
    export_links_to_csv,
    export_links_to_json,
    json_import,
    txt_import,
)

app = Typer(no_args_is_help=True)
logger = Logger(__name__)


@app.command(name="get", help="Get a configuration value")
def get_config(
    key: str = Argument(..., help="Configuration key to retrieve"),
) -> None:
    """Get a specific configuration value."""
    value = config_manager.get_setting(key)
    if value is None:
        logger.error(f"Configuration key '{key}' not found.")
        return

    logger.print(f"[bold cyan]{key}[/bold cyan]: {value}")


@app.command(name="set", help="Set a configuration value")
def set_config(
    key: str = Argument(..., help="Configuration key to set"),
    value: str = Argument(..., help="Configuration value to set"),
) -> None:
    """Set a specific configuration value."""
    # Try to parse the value as JSON first for complex types
    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        # If it's not valid JSON, treat it as a string
        parsed_value = value

    # Handle boolean conversion
    if isinstance(parsed_value, str) and parsed_value.lower() in ("true", "false"):
        parsed_value = parsed_value.lower() == "true"

    if config_manager.set_setting(key, parsed_value):
        logger.print(f"[green]Successfully set[/green] [bold cyan]{key}[/bold cyan] = {parsed_value}")
    else:
        logger.error(f"Failed to set configuration key '{key}'. Key may not exist.")


@app.command(name="list", help="List all configuration values")
def list_config() -> None:
    """List all configuration values."""
    config_dict = config_manager.get_config_dict()

    table = Table(title="Configuration")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Type", style="green")

    for key, value in config_dict.items():
        # Format lists nicely
        formatted_value = ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)

        table.add_row(key, formatted_value, type(value).__name__)

    logger.print(table)


@app.command(name="reset", help="Reset configuration to defaults")
def reset_config() -> None:
    """Reset configuration to default values."""
    config_manager.reset_config()
    logger.print("[green]Configuration reset to defaults successfully.[/green]")


@app.command(name="path", help="Show configuration file path")
def show_config_path() -> None:
    """Show the path to the configuration file."""
    config_path = config_manager.get_config_file_path()
    logger.print(f"Configuration file: [bold cyan]{config_path}[/bold cyan]")


@app.command(name="edit", help="Show configuration for manual editing")
def edit_config() -> None:
    """Show current configuration in JSON format for manual editing."""
    config_dict = config_manager.get_config_dict()
    formatted_config = json.dumps(config_dict, indent=2)

    logger.print("[bold]Current configuration:[/bold]")
    logger.print(f"[dim]{formatted_config}[/dim]")
    logger.print(
        f"\n[yellow]To edit manually, modify:[/yellow] [bold cyan]{config_manager.get_config_file_path()}[/bold cyan]",
    )


@app.command(name="import", help="Import links from a TXT, CSV, or JSON file.")
def import_links(
    file_path: str = Option(..., help="Path to the file to import."),
) -> None:
    try:
        check_file(file_path)
    except Exception as e:
        logger.exception(f"Error checking file: {e}")
        return
    extension = path.splitext(file_path)[1].lower()

    if extension == ".txt":
        txt_import(file_path)
    elif extension == ".csv":
        csv_import(file_path)
    elif extension == ".json":
        json_import(file_path)
    else:
        logger.error(f"Unsupported file extension: {extension}")


@app.command(name="export", help="Export links to a JSON or CSV file.")
def export_links(
    format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
    output: str = Option("links_export.json", "--output", "-o", help="Output file path", show_default=True),
) -> None:
    format = format.lower()
    try:
        if format == "json":
            export_links_to_json(output)
        elif format == "csv":
            export_links_to_csv(output)
        else:
            logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
            raise Exit(code=1)
    except Exception as e:
        logger.exception(f"Error exporting links: {e}")
        raise Exit(code=1)


@app.command(name="backup", help="Export all links to JSON or CSV files.")
def export_all_command(
    format: str = Option(
        "json",
        "--format",
        "-f",
        help="Export format: json or csv",
        show_default=True,
    ),
    output_dir: str | None = Option(None, "--output-dir", "-d", help="Directory to store exported files."),
) -> None:
    format = format.lower()
    if format not in {"json", "csv"}:
        logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
        raise Exit(code=1)

    if not output_dir:
        output_dir_path = Path.cwd()
    else:
        output_dir_path = Path(output_dir)
        try:
            output_dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.exception(f"Failed to create directory '{output_dir_path}': {e}")
            raise Exit(code=1)

    links_output = output_dir_path / f"links_export.{format}"

    try:
        if format == "json":
            export_links_to_json(str(links_output))
        else:  # csv
            export_links_to_csv(str(links_output))
        logger.info(f"Exported all links successfully to '{links_output}'.")
    except Exception as e:
        logger.exception(f"Error exporting links: {e}")
        raise Exit(code=1)


@app.command(help="Add a new link to the database.")
def create(
    url: str | None = Option(None, help="URL of the link."),
    domain: str | None = Option(None, help="Domain of the link."),
    description: str | None = Option("", help="Description of the link."),
    tags: list[str] = Option([], "--tag", "-t", help="Tags associated with the link."),
    is_read: bool = Option(False, "--is-read", "-r", help="Mark the link as read or unread."),
) -> None:
    if not url:
        url = prompt("URL of the link")
    if not domain:
        domain = prompt("Domain of the link")

    link = link_service.create_link(
        url=url,
        description=description,
        domain=domain,
        tag=", ".join(tags) if isinstance(tags, list) else tags,
        is_read=is_read,
    )
    if link:
        logger.info(f"Link added with ID: {link.id}")
    else:
        logger.error("Failed to add link.")


@app.command(name="list", help="List all links.")
def list_link() -> None:
    if not (links := link_service.get_links()):
        logger.warning("No links found.")
        return

    for link in links:
        logger.info(f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, Tags: {link.tag}")


@app.command(help="Search for links based on various filters.")
def search(
    domain: str | None = Option(None, help="Filter by domain."),
    url: str | None = Option(None, help="Filter by URL."),
    tags: list[str] = Option([], "--tag", "-t", help="Tags to filter by."),
    description: str | None = Option(None, help="Filter by description."),
    sort_by: str | None = Option(None, help="Field to sort by (e.g. created_at, updated_at, domain)."),
    sort_order: str = Option("ASC", help="Sort order: ASC or DESC."),
    limit: int = Option(3, help="Number of results to return."),
    offset: int = Option(0, help="Number of results to skip."),
    is_read: bool | None = Option(None, help="Filter by read status."),
) -> None:
    criteria = {
        "domain": domain,
        "url": url,
        "tag": tags,
        "description": description,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "limit": limit,
        "offset": offset,
        "is_read": is_read,
    }
    criteria = {k: v for k, v in criteria.items() if v not in [None, [], ""]}
    results = link_service.search_links(criteria)
    if not results:
        logger.warning("No matching links found.")
        return
    for link in results:
        logger.info(
            f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, "
            f"Description: {link.description}, Tags: {link.tag}, Read: {link.is_read}",
        )


@app.command(help="Delete a link by its ID.")
def delete(link_id: int = Option(..., help="ID of the link to delete.")) -> None:
    try:
        link_service.delete_link(link_id)
        logger.info(f"Link with ID {link_id} has been deleted.")
    except Exception as e:
        logger.exception(f"Failed to delete link with ID {link_id}: {e}")


@app.command(help="Update a link's details by its ID.")
def update(
    link_id: list[int] = Option(..., help="ID of the link's to update."),
    url: str | None = Option(None, help="New URL of the link."),
    domain: str | None = Option(None, help="New domain of the link."),
    description: str | None = Option(None, help="New description of the link."),
    tags: list[str] | None = Option(None, "--tag", "-t", help="New tags for the link."),
    is_read: bool | None = Option(None, "--is-read", "-r", help="Mark as read or unread."),
) -> None:
    # Collect data to update
    update_data = {}
    if url:
        update_data["url"] = url
    if domain:
        update_data["domain"] = domain
    if description is not None:
        update_data["description"] = description
    if tags is not None:
        update_data["tag"] = ", ".join(tags) if isinstance(tags, list) else tags
    if is_read is not None:
        update_data["is_read"] = is_read

    # Perform the update
    for lid in link_id:
        # Check if link exists
        if not link_service.get_link(lid):
            logger.error(f"No link found with ID {lid}.")
            continue

        try:
            if link_service.update_link(lid, **update_data):
                logger.info(f"Link with ID {lid} has been updated.")
            else:
                logger.error(f"Failed to update link with ID {lid}.")
        except Exception as e:
            logger.exception(f"Failed to update link with ID {lid}: {e}")


@app.command(help="Show a specific link by its ID.")
def show(link_id: int = Option(..., help="ID of the link to show.")) -> None:
    if link := link_service.get_link(link_id):
        logger.info(
            f"ID: {link.id}\n"
            f"URL: {link.url}\n"
            f"Domain: {link.domain}\n"
            f"Description: {link.description}\n"
            f"Tags: {link.tag}\n"
            f"Read: {link.is_read}\n"
            f"Created: {link.created_at}\n"
            f"Updated: {link.updated_at}",
        )
    else:
        logger.error(f"No link found with ID {link_id}.")


@app.command(name="show", help="Show version information")
def show_version() -> None:
    """Show the current version of LinkCovery."""
    try:
        version = importlib.metadata.version("linkcovery")
        logger.print(f"[bold cyan]LinkCovery[/bold cyan] version [bold green]{version}[/bold green]")
    except importlib.metadata.PackageNotFoundError:
        logger.print("[yellow]Version information not available (development mode)[/yellow]")


@app.callback(invoke_without_command=True)
def version_callback() -> None:
    """Default callback that shows version when no subcommand is provided."""
    show_version()
