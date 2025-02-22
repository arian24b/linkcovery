from typer import Typer, Option, Exit, prompt

from app.core.logger import AppLogger
from app.core.database import user_service, link_service

logger = AppLogger(__name__)
app = Typer()


@app.command(help="Add a new link to the database.")
def create(
    url: str | None = Option(None, help="URL of the link."),
    domain: str | None = Option(None, help="Domain of the link."),
    author_email: str | None = Option(None, help="Email of the author."),
    description: str | None = Option("", help="Description of the link."),
    tags: list[str] = Option([], "--tag", "-t", help="Tags associated with the link."),
    is_read: bool = Option(False, "--is-read", "-r", help="Mark the link as read or unread."),
) -> None:
    if not url:
        url = prompt("URL of the link")
    if not domain:
        domain = prompt("Domain of the link")
    if not author_email:
        author_email = prompt("Author's email")
    if not (user := user_service.get_user(user_email=author_email)):
        logger.error(f"Author with email '{author_email}' does not exist.")
        raise Exit(code=1)

    link_id = link_service.create_link(
        url=url,
        description=description,
        domain=domain,
        tag=", ".join(tags) if isinstance(tags, list) else tags,
        author_id=user.id,
        is_read=is_read,
    )
    if link_id:
        logger.info(f"Link added with ID: {link_id}")
    else:
        logger.error("Failed to add link.")


@app.command(help="List all links with their authors.")
def list_link() -> None:
    if not (links := link_service.get_links()):
        logger.warning("No links found.")
        return

    for link in links:
        logger.info(f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, Author: {link.author}")


@app.command(help="Search for links based on various filters.")
def search(
    domain: str | None = Option(None, help="Filter by domain."),
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
            f"Description: {link.description}, Tags: {link.tag}, Read: {link.is_read}"
        )


@app.command(help="Delete a link by its ID.")
def delete(link_id: int = Option(..., help="ID of the link to delete.")) -> None:
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
    is_read: bool | None = Option(None, "--is-read", "-r", help="Mark as read or unread."),
) -> None:
    # Check if link exists
    if not link_service.get_link(link_id):
        logger.error(f"No link found with ID {link_id}.")
        raise Exit(code=1)

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
    if link_service.update_link(link_id, **update_data):
        logger.info(f"Link with ID {link_id} has been updated.")
    else:
        logger.error(f"Failed to update link with ID {link_id}.")


@app.command("read-link", help="Mark 3 links as read for a given author.")
def mark_links_as_read(author_id: int = Option(..., help="ID of the author")) -> None:
    if not (links := link_service.get_links_by_author(author_id=author_id, number=3)):
        logger.warning("No links found to update.")
        return

    link_ids = [link.id for link in links if link.id is not None]
    link_service.update_is_read_for_links(link_ids)

    for link in links:
        logger.info(f"Marked link {link.id} as read: {link.url}")
