from typer import Option, Typer, prompt

from linkcovery.core.database import link_service
from linkcovery.core.logger import Logger

logger = Logger(__name__)
app = Typer(no_args_is_help=True)


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
