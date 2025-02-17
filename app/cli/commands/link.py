from typer import Typer, Option, Exit, prompt
from datetime import datetime, UTC

from app.core.logger import AppLogger
from app.core.database import user_service, link_service, Link


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

    if not (user := user_service.get_user(user_email=author_email)):
        logger.error(f"Author with email '{author_email}' does not exist.")
        raise Exit(code=1)

    link = Link(
        url=url,
        description=description,
        domain=domain,
        tag=tags,
        author_id=user.id,
    )

    if link_id := link_service.create_link(link):
        logger.info(f"Link added with ID: {link_id}")
    else:
        logger.error("Failed to add link.")


@app.command(help="List all links with their authors.")
def list_link() -> None:
    """
    List all links with their authors.
    """
    if not (links := link_service.get_links()):
        logger.warning("No links found.")
        return None

    for entry in links:
        link: Link = entry["link"]
        logger.info(f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, Author: {link.author}")


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
    results = link_service.search_links(
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
    if link_service.delete_link(link_id):
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

    if not (existing_link := link_service.get_link(link_id)):
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

    if link_service.update_link(link_id, existing_link):
        logger.info(f"Link with ID {link_id} has been updated.")
    else:
        logger.error(f"Failed to update link with ID {link_id}.")


@app.command("read-link", help="Mark 3 links as read.")
def mark_links_as_read(auther_id: str | None = Option(None)) -> None:
    """
    Retrieve 3 links from the database and mark them as read (is_read = 1).
    """
    if not (links := link_service.get_links_by_author(author_id=auther_id, number=3)):
        logger.warning("No links found to update.")
        return

    link_ids = [link.id for link in links if link.id is not None]
    link_service.update_is_read_for_links(link_ids)

    for link in links:
        logger.info(f"Marked link {link.id} as read: {link.url}")
