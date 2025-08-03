from csv import DictReader, DictWriter
from json import JSONDecodeError, dump, load
from os import path
from urllib.parse import urlparse

from pydantic import HttpUrl, ValidationError, parse_obj_as
from rich.progress import track

from linkcovery.core.database import link_service
from linkcovery.core.logger import Logger
from linkcovery.core.settings import config_manager

logger = Logger(__name__)


def check_file(file_path: str) -> bool:
    if not path.exists(file_path):
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)

    extension = path.splitext(file_path)[1].lower()
    allowed_extensions = config_manager.config.allowed_extensions
    if extension not in allowed_extensions:
        msg = f"Invalid file extension: {extension}. Allowed extensions: {allowed_extensions}"
        raise ValueError(msg)

    return True


def get_description(text: str | None) -> str:
    return text or ""


def txt_import(file_path: str) -> None:
    with open(file_path, encoding="utf-8") as content:
        links = [line.strip() for line in content if line.strip()]
        if not links:
            logger.info("No links found in the TXT file.")
            return

    added_link = 0
    for line_number, link in enumerate(links, start=1):
        try:
            url = str(parse_obj_as(HttpUrl, link))
            domain = urlparse(url).netloc
            tags = ", ".join(domain.split("."))
            link_service.create_link(
                url=url,
                description=get_description(None),
                domain=domain,
                tag=tags,
            )
            added_link += 1
        except (ValidationError, Exception) as e:
            logger.exception(f"Failed to add link at line {line_number}. Error: {e}")

    logger.info(f"Successfully imported {added_link} links from TXT file.")


def csv_import(file_path: str) -> None:
    with open(file_path, encoding="utf-8") as content:
        reader = DictReader(content)
        if not reader.fieldnames:
            logger.info("CSV file is empty or invalid.")
            return

        required_fields = {"url", "domain", "description", "tag", "is_read"}
        if not required_fields.issubset(reader.fieldnames):
            logger.info(f"CSV file is missing required fields. Required fields: {required_fields}")
            return

        links = list(reader)
        if not links:
            logger.info("No links found in the CSV file.")
            return

    added_link = 0
    for line_number, row in enumerate(links, start=2):
        try:
            url = str(parse_obj_as(HttpUrl, row["url"]))
            domain = row.get("domain") or urlparse(url).netloc
            tags = row.get("tag") or ", ".join(domain.split("."))
            is_read = str(row.get("is_read", "False")).strip().lower() in {"1", "true", "yes"}
            link_service.create_link(
                url=url,
                description=get_description(row.get("description")),
                domain=domain,
                tag=tags,
                is_read=is_read,
            )
            added_link += 1
        except (ValidationError, Exception) as e:
            logger.exception(f"Failed to add link at line {line_number}. Error: {e}")

    logger.info(f"Successfully imported {added_link} links from CSV file.")


def json_import(file_path: str) -> None:
    try:
        with open(file_path, encoding="utf-8") as f:
            links_data = load(f)
    except JSONDecodeError as e:
        logger.exception(f"Invalid JSON format: {e}")
        return
    except Exception as e:
        logger.exception(f"Failed to open JSON file: {e}")
        return

    if not links_data:
        logger.info("No links found in the JSON file.")
        return

    added_link = 0
    for index, link_dict in enumerate(links_data, start=1):
        try:
            url = str(parse_obj_as(HttpUrl, link_dict["url"]))
            domain = link_dict.get("domain") or urlparse(url).netloc
            tags = link_dict.get("tag") or ", ".join(domain.split("."))
            description = get_description(link_dict.get("description"))
            is_read = link_dict.get("is_read", False)
            link_service.create_link(
                url=url,
                description=description,
                domain=domain,
                tag=tags,
                is_read=is_read,
            )
            added_link += 1
        except (ValidationError, Exception) as e:
            logger.exception(f"Failed to add link at index {index} from JSON. Error: {e}")

    logger.info(f"Successfully imported {added_link} links from JSON file.")


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
