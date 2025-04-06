from typer import Exit, Option, Typer, prompt

from app.core.database import link_service, user_service
from app.core.logger import AppLogger

logger = AppLogger(__name__)
app = Typer(no_args_is_help=True)


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


@app.command(name="list", help="List all links with their authors.")
def list_link() -> None:
    if not (links := link_service.get_links()):
        logger.warning("No links found.")
        return

    for link in links:
        logger.info(
            f"ID: {link.id}, Domain: {link.domain}, URL: {link.url}, Description: {link.description}, Author: {link.author.name}",
        )


@app.command(help="Search for links based on various filters.")
def search(
    id: int | None = Option(None, help="Filter by link ID."),
    author_id: int | None = Option(None, help="Filter by author ID."),
    domain: str | None = Option(None, help="Filter by domain."),
    url: str | None = Option(None, help="Filter by URL."),
    tags: list[str] = Option([], "--tag", "-t", help="Tags to filter by."),
    description: str | None = Option(None, help="Filter by description."),
    sort_by: str | None = Option(None, help="Field to sort by (e.g. created_at, updated_at, domain)."),
    sort_order: str = Option("ASC", help="Sort order: ASC or DESC."),
    limit: int = Option(3, help="Number of results to return."),
    offset: int = Option(0, help="Number of results to skip."),
    is_read: bool | None = Option(None, help="Filter by read status."),
    feilds: list[str] = Option(
        ["id", "url", "domain", "description", "tag", "is_read"],
        "--fields",
        "-f",
        help="Fields to display in the results.",
    ),
) -> None:
    criteria = {
        "id": id,
        "author_id": author_id,
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
        # Prepare the output based on requested fields
        output_parts = []
        for field in feilds:
            if field == "id" and hasattr(link, "id"):
                output_parts.append(f"ID: {link.id}")
            elif field == "url" and hasattr(link, "url"):
                output_parts.append(f"URL: {link.url}")
            elif field == "domain" and hasattr(link, "domain"):
                output_parts.append(f"Domain: {link.domain}")
            elif field == "description" and hasattr(link, "description"):
                output_parts.append(f"Description: {link.description}")
            elif field == "tag" and hasattr(link, "tag"):
                output_parts.append(f"Tags: {link.tag}")
            elif field == "is_read" and hasattr(link, "is_read"):
                output_parts.append(f"Read: {link.is_read}")

        logger.info(", ".join(output_parts))


@app.command(help="Delete a link by its ID.")
def delete(link_id: int = Option(..., help="ID of the link to delete.")) -> None:
    if link_service.delete_link(link_id):
        logger.info(f"Link with ID {link_id} has been deleted.")
    else:
        logger.error(f"Failed to delete link with ID {link_id}.")


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

        if link_service.update_link(lid, **update_data):
            logger.info(f"Link with ID {lid} has been updated.")
        else:
            logger.error(f"Failed to update link with ID {lid}.")


@app.command(name="read", help="Mark 3 links as read for a given author.")
def read_link(author_id: int = Option(..., help="ID of the author")) -> None:
    if not (links := link_service.get_links_by_author(author_id, 3)):
        logger.warning("No links found for the author.")
        return

    for link in links:
        if link_service.update_link(link.id, is_read=True):
            logger.info(f"Link with ID {link.id} marked as read.")
        else:
            logger.error(f"Failed to mark link with ID {link.id} as read.")
