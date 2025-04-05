from typer import Typer

from app.core.logger import AppLogger
from app.core.database import link_service
from app.core.fetch_description import fetch_description


logger = AppLogger(__name__)
app = Typer(no_args_is_help=True)


@app.command(help="Add a new link to the database.")
def update_link_description() -> None:
    for link in link_service.get_links():
        if link.description == "Imported from TXT" or not link.description:
            if description := fetch_description(link.url):
                link_service.update_link(link.id, description=description)
                logger.info(f"Link {link.id} updated with fetched description.")
            else:
                logger.error(f"Failed to fetch description for link {link.id}.")
    logger.info("All links processed.")
