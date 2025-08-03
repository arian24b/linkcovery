from csv import DictWriter
from json import dump

from rich.progress import track

from app.core.database import link_service
from app.core.logger import AppLogger

logger = AppLogger(__name__)


def export_links_to_json(output_path: str) -> None:
    """Export all links to JSON format."""
    links = link_service.get_links()
    links_data = []
    for link in links:
        link_data = {col.name: getattr(link, col.name) for col in link.__table__.columns}
        links_data.append(link_data)

    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            dump(links_data, json_file, indent=4)
        logger.info(f"Successfully exported {len(links_data)} links to {output_path}.")
    except Exception as e:
        logger.exception(f"Failed to export links to JSON: {e}")


def export_links_to_csv(output_path: str) -> None:
    """Export all links to CSV format."""
    links = link_service.get_links()
    if not links:
        logger.warning("No links available to export.")
        return

    headers = [col.name for col in links[0].__table__.columns]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for link in track(links, description="Exporting links..."):
                row = {col.name: getattr(link, col.name) for col in link.__table__.columns}
                writer.writerow(row)
        logger.info(f"Successfully exported {len(links)} links to {output_path}.")
    except Exception as e:
        logger.exception(f"Failed to export links to CSV: {e}")
