from pydantic import HttpUrl
from urllib.parse import urlparse
from csv import DictReader
from json import JSONDecodeError, load

from app.core.logger import AppLogger
from app.core.utils import get_description
from app.core.database import link_service


logger = AppLogger(__name__)


def txt_import(file_path: str, author_id: int):
    with open(file_path, "r", encoding="utf-8") as content:
        if not (links := [line.strip() for line in content if line.strip()]):
            logger.info("No links found in the TXT file.")
            return

    added_link = 0

    for line_number, link in enumerate(links, start=1):
        url = str(HttpUrl(link))
        domain = urlparse(url).netloc
        tags = ",".join(domain.split("."))

        try:
            link_service.create_link(
                url=url,
                description=get_description(None),
                domain=domain,
                tag=tags,
                author_id=author_id,
            )
            added_link += 1
        except Exception as e:
            logger.error(f"Failed to add link {line_number}.\nError: {e}")

    logger.info(f"Successfully imported {added_link} links from TXT file for user {author_id}.")


def csv_import(file_path: str, author_id: int):
    with open(file_path, "r", encoding="utf-8") as content:
        reader = DictReader(content)

        if not reader.fieldnames:
            logger.info("CSV file is empty or invalid.")
            return

        required_fields = {"url", "domain", "description", "tag", "is_read"}
        if not required_fields.issubset(reader.fieldnames):
            logger.info(f"CSV file is missing required fields. Required fields: {required_fields}")
            return

        if not (links := list(reader)):
            logger.info("No links found in the CSV file.")
            return

    added_link = 0

    for line_number, row in enumerate(links, start=2):
        try:
            url = str(HttpUrl(row["url"]))
            domain = row.get("domain", urlparse(url).netloc)
            # Handle tags: split by comma and join them with commas (or adjust as needed)
            tags = (
                ",".join(tag.strip() for tag in row["tag"].split(","))
                if row.get("tag")
                else ",".join(domain.split("."))
            )
            is_read = row.get("is_read", "False").strip().lower() in {"1", "true", "yes"}

            # Pass keyword arguments instead of a Link instance:
            link_service.create_link(
                url=url,
                description=get_description(row.get("description")),
                domain=domain,
                tag=tags,
                author_id=author_id,
                is_read=is_read,
            )
            added_link += 1
        except Exception as e:
            logger.error(f"Failed to add link at line {line_number}.\nError: {e}")

    logger.info(f"Successfully imported {added_link} links from CSV file for user {author_id}.")


def json_import(file_path: str, author_id: int):
    """
    Import links from a JSON file.

    The JSON file is expected to contain a list of dictionaries,
    each with at least a "url" key and optionally "domain", "description", "tag", and "is_read".
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            links_data = load(f)
    except JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return
    except Exception as e:
        logger.error(f"Failed to open JSON file: {e}")
        return

    if not links_data:
        logger.info("No links found in the JSON file.")
        return

    added_link = 0

    for index, link_dict in enumerate(links_data, start=1):
        try:
            url = str(HttpUrl(link_dict["url"]))
            domain = link_dict.get("domain", urlparse(url).netloc)
            # If no tag is provided, generate one from the domain
            tags = link_dict.get("tag")
            if not tags:
                tags = ",".join(domain.split("."))
            description = get_description(link_dict.get("description"))
            is_read = link_dict.get("is_read", False)

            link_service.create_link(
                url=url,
                description=description,
                domain=domain,
                tag=tags,
                author_id=author_id,
                is_read=is_read,
            )
            added_link += 1
        except Exception as e:
            logger.error(f"Failed to add link at index {index} from JSON. Error: {e}")

    logger.info(f"Successfully imported {added_link} links from JSON file for user {author_id}.")
