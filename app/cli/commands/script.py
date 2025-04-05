from typer import Typer

from app.core.database import link_service
from app.core.fetch_description import fetch_description
from app.core.logger import AppLogger

logger = AppLogger(__name__)
app = Typer(no_args_is_help=True)


@app.command(help="Add a new link to the database.")
def update_link_description() -> None:
    updated_links = []

    for link in link_service.get_links():
        if link.description == "Imported from TXT" or not link.description:
            if description := fetch_description(link.url):
                link_service.update_link(link.id, description=description)
                updated_links.append(link.id)
            else:
                logger.error(f"Failed to fetch description for link {link.id}.")
    logger.info(f"Total links updated: {len(updated_links)}\n Links updated:\n{updated_links}")


@app.command(help="remove www from domain, change http:// to https://.")
def update_link_domain() -> None:
    updated_links = []

    for link in link_service.get_links():
        if link.domain.startswith("www."):
            new_domain = link.domain[4:]
            link_service.update_link(link.id, domain=new_domain)
            updated_links.append(link.id)
        elif link.domain.startswith("http://"):
            new_domain = "https://" + link.domain[7:]
            link_service.update_link(link.id, domain=new_domain)
            updated_links.append(link.id)

    logger.info(f"Total links updated: {len(updated_links)}\n Links updated:\n{updated_links}")
