#!/usr/bin/env python3

from typer import Option, Exit, prompt
from datetime import datetime, UTC
from os import path
from pathlib import Path
from json import load

from main import app, db
from database import User, Link
from importer import check_file, import_txt, import_csv, import_links_from_json
from exporter import export_users_to_json, export_users_to_csv, export_links_to_json, export_links_to_csv, export_all
from logger import Logger

logger = Logger(__name__)


# User Commands
@app.command("user-add", help="Add a new user to the database.")
def add_user(
    name: str = Option(..., prompt=True, help="Name of the user."),
    email: str = Option(..., prompt=True, help="Email of the user."),
) -> None:
    """
    Add a new user to the database.
    """
    user = User(
        id=None,
        name=name,
        email=email,
    )

    if user_id := db.create_user(user):
        logger.info(f"User '{name}' added with ID: {user_id}")
    else:
        logger.error(f"Failed to add user '{name}'.")


@app.command("user-list", help="List all users.")
def list_users() -> None:
    """
    List all users.
    """
    if not (users := db.read_users()):
        logger.warning("No users found.")
        return None
    for user in users:
        logger.info(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")


# Link Commands
@app.command("link-add", help="Add a new link to the database.")
def add_link(
    url: str | None = Option(None, help="URL of the link."),
    domain: str | None = Option(None, help="Domain of the link."),
    author_email: str | None = Option(None, help="Email of the author."),
    description: str | None = Option("", help="Description of the link."),
    tags: list[str] = Option([], "--tag", "-t", help="Tags associated with the link."),
) -> None:
    """
    Add a new link to the database.
    """
    if not url:
        url = prompt("URL of the link")
    if not domain:
        domain = prompt("Domain of the link")
    if not author_email:
        author_email = prompt("Author's email")

    user = db.get_user_by_email(author_email)
    if not user:
        logger.error(f"Author with email '{author_email}' does not exist.")
        raise Exit(code=1)

    link = Link(
        id=None,
        url=url,
        domain=domain,
        description=description,
        tag=tags,
        author_id=user.id,
    )

    if link_id := db.create_link(link):
        logger.info(f"Link added with ID: {link_id}")
    else:
        logger.error("Failed to add link.")


@app.command("link-list", help="List all links with their authors.")
def list_links() -> None:
    """
    List all links with their authors.
    """
    links_with_authors = db.read_links_with_authors()
    if not links_with_authors:
        logger.warning("No links found.")
        return None
    for entry in links_with_authors:
        link: Link = entry["link"]
        author = entry["author"]
        logger.info(
            f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, Author: {author['name']} ({author['email']})"
        )


@app.command("link-search", help="Search for links based on domain, tags, or description.")
def search_links(
    domain: str | None = Option(None, help="Filter by domain."),
    tags: list[str] = Option([], "--tag", "-t", help="Tags to filter by."),
    description: str | None = Option(None, help="Filter by description."),
    sort_by: str = Option("created_at", help="Field to sort by."),
    sort_order: str = Option("ASC", help="Sort order: ASC or DESC."),
    limit: int = Option(3, help="Number of results to return."),
    offset: int = Option(0, help="Number of results to skip."),
    is_read: bool | None = Option(None, help="Filter by read status."),
) -> None:
    """
    Search for links based on domain, tags, or description.
    """
    results = db.search_links(
        domain=domain,
        tags=tags,
        description=description,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
        is_read=is_read,
    )
    if not results:
        logger.warning("No matching links found.")
        return None
    for link in results:
        logger.info(
            f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, Description: {link.description}, Tags: {', '.join(link.tag)}"
        )


@app.command("link-delete", help="Delete a link by its ID.")
def delete_link(link_id: int = Option(..., help="ID of the link to delete.")) -> None:
    """
    Delete a link by its ID.
    """
    if db.delete_link(link_id):
        logger.info(f"Link with ID {link_id} has been deleted.")
    else:
        logger.error(f"Failed to delete link with ID {link_id}.")


@app.command("link-update", help="Update a link's details by its ID.")
def update_link(
    link_id: int = Option(..., help="ID of the link to update."),
    url: str | None = Option(None, help="New URL of the link."),
    domain: str | None = Option(None, help="New domain of the link."),
    description: str | None = Option(None, help="New description of the link."),
    tags: list[str] | None = Option(None, "--tag", "-t", help="New tags for the link."),
    is_read: bool | None = Option(None, help="Mark as read or unread."),
) -> None:
    """
    Update a link's details by its ID.
    """
    existing_link = db.read_link(link_id)
    if not existing_link:
        logger.error(f"No link found with ID {link_id}.")
        raise Exit(code=1)

    if url is None and domain is None and description is None and tags is None and is_read is None:
        logger.warning("No updates provided. Use options to specify fields to update.")
        raise Exit()

    if url:
        existing_link.url = url
    if domain:
        existing_link.domain = domain
    if description is not None:
        existing_link.description = description
    if tags is not None:
        existing_link.tag = tags
    if is_read is not None:
        existing_link.is_read = is_read

    existing_link.updated_at = datetime.now(UTC).isoformat()

    if db.update_link(link_id, existing_link):
        logger.info(f"Link with ID {link_id} has been updated.")
    else:
        logger.error(f"Failed to update link with ID {link_id}.")


@app.command("link-mark-read", help="Mark 3 links as read.")
def mark_links_as_read() -> None:
    """
    Retrieve 3 links from the database and mark them as read (is_read = 1).
    """
    links = db.read_links(limit=3)
    if not links:
        logger.warning("No links found to update.")
        return

    link_ids = [link.id for link in links if link.id is not None]
    db.update_is_read_for_links(link_ids)

    for link in links:
        logger.info(f"Marked link {link.id} as read: {link.url}")


# Import/Export Commands
@app.command("import", help="Import links from a TXT or CSV file.")
def import_links(
    file_path: str = Option(..., help="Path to the .txt or .csv file to import."),
    author_id: int = Option(..., help="ID of the author to associate with the imported links."),
) -> None:
    """
    Import links from a TXT or CSV file into the database.
    """
    try:
        if check_file(file_path):
            extension = path.splitext(file_path)[1].lower()
            try:
                if extension == ".txt":
                    import_txt(file_path, author_id, db)
                elif extension == ".csv":
                    import_csv(file_path, author_id, db)
                elif extension == ".json":
                    with open(file_path, "r", encoding="utf-8") as json_file:
                        data = load(json_file)
                        if isinstance(data, list) and all("url" in item for item in data):
                            import_links_from_json(file_path, db)
                else:
                    logger.error(f"Unsupported file extension: {extension}")
            except Exception as e:
                logger.error(f"Import failed: {e}")
    except FileNotFoundError as fnf_error:
        logger.error(f"{fnf_error}")
        raise Exit(code=1)
    except ValueError as val_error:
        logger.error(f"{val_error}")
        raise Exit(code=1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise Exit(code=1)


@app.command("export-users", help="Export all users to a JSON or CSV file.")
def export_users(
    format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
    output: str = Option("users_export.json", "--output", "-o", help="Output file path", show_default=True),
) -> None:
    """
    Export all users to the specified format (JSON or CSV).
    """
    format = format.lower()
    if format == "json":
        export_users_to_json(db, output)
    elif format == "csv":
        export_users_to_csv(db, output)
    else:
        logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")


@app.command("export-links", help="Export all links to a JSON or CSV file.")
def export_links(
    format: str = Option("json", "--format", "-f", help="Export format: json or csv", show_default=True),
    output: str = Option("links_export.json", "--output", "-o", help="Output file path", show_default=True),
) -> None:
    """
    Export all links to the specified format (JSON or CSV).
    """
    format = format.lower()
    if format == "json":
        export_links_to_json(db, output)
    elif format == "csv":
        export_links_to_csv(db, output)
    else:
        logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")


@app.command("export-all", help="Export all users and links to JSON or CSV files.")
def export_all_command(
    format: str = Option(
        "json", "--format", "-f", help="Export format for both users and links: json or csv", show_default=True
    ),
    output_dir: str | None = Option(None, "--output-dir", "-d", help="Directory to store exported files."),
) -> None:
    """
    Export all users and links to the specified format (JSON or CSV) within a directory.
    """
    format = format.lower()
    if format not in {"json", "csv"}:
        logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
        raise Exit(code=1)

    if not output_dir:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory '{output_dir}': {e}")
            raise Exit(code=1)

    users_output = output_dir / f"users_export.{format}"
    links_output = output_dir / f"links_export.{format}"

    for output_path in [users_output, links_output]:
        if output_path.exists():
            overwrite = prompt(f"File '{output_path}' already exists. Overwrite? (y/n)", default="n")
            if overwrite.lower() != "y":
                logger.warning(f"Skipped exporting to '{output_path}'.")
                raise Exit()

    export_all(db, format, str(output_dir))


@app.command("test-log")
def test_log() -> None:
    """
    Test logging functionality.
    """
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")


if __name__ == "__main__":
    app()
