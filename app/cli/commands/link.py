from typer import Typer, Option, Exit, prompt
from datetime import datetime, UTC

from app.core.logger import AppLogger
from app.core.models import Link, db


logger = AppLogger(__name__)

app = Typer()


@app.command(help="Add a new link to the database.")
def create(
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


@app.command(help="List all links with their authors.")
def list_link() -> None:
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


@app.command(help="Search for links based on domain, tags, or description.")
def search(
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


@app.command(help="Delete a link by its ID.")
def delete(link_id: int = Option(..., help="ID of the link to delete.")) -> None:
    """
    Delete a link by its ID.
    """
    if db.delete_link(link_id):
        logger.info(f"Link with ID {link_id} has been deleted.")
    else:
        logger.error(f"Failed to delete link with ID {link_id}.")


@app.command(help="Update a link's details by its ID.")
def update(
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
