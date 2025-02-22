from pydantic import HttpUrl
from urllib.parse import urlparse
from csv import DictReader
# from json import JSONDecodeError, load

from app.core.logger import AppLogger
from app.core.utils import get_description
from app.core.database import link_service, Link


logger = AppLogger(__name__)


def txt(file_path: str, author_id: int):
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


def csv(file_path: str, author_id: int):
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


# TODO:add import json
# def json(file_path: str, author_id: int):
#     with open(file_path, "r", encoding="utf-8") as json_file:
#         if not (links_data := load(json_file)):
#             logger.info("No links found in the JSON file.")
#             return


#         new_links = []
#         for index, link_dict in enumerate(links_data, start=1):
#             try:
#                 # Extract author_email to find or create the user
#                 author_info = link_dict.pop("author", {})
#                 author_email = author_info.get("email")
#                 if not author_email:
#                     print(f"[red]Link {index}: Missing author email. Skipping.[/red]")
#                     continue

#                 user = db.get_user_by_email(author_email)
#                 if not user:
#                     # Optionally, create the user if they don't exist
#                     user = User(name=author_info.get("name", "Unknown"), email=author_email)
#                     user_id = db.create_user(user)
#                     if not user_id:
#                         print(f"[red]Link {index}: Failed to create user '{author_email}'. Skipping link.[/red]")
#                         continue
#                     user.id = user_id

#                 # Prepare Link object
#                 link_obj = Link(**link_dict)
#                 link_obj.author_id = user.id

#                 # Check if link already exists
#                 existing_link = db.read_link_by_url(link_obj.url)
#                 if existing_link:
#                     print(f"[yellow]Link with URL '{link_obj.url}' already exists. Skipping.[/yellow]")
#                     continue

#                 new_links.append(link_obj)
#             except ValidationError as ve:
#                 print(f"[red]Link {index}: Validation error: {ve}[/red]")
#                 raise  # Trigger transaction rollback
#             except Exception as e:
#                 print(f"[red]Link {index}: Failed to prepare link. Error: {e}[/red]")
#                 raise  # Trigger transaction rollback

#         if new_links:
#             db.bulk_create_links(new_links)
#             print(f"[green]Successfully imported {len(new_links)} links from JSON file.[/green]")
#         else:
#             print("[yellow]No new links to import.[/yellow]")

#     except JSONDecodeError as jde:
#         print(f"[red]Invalid JSON format: {jde}[/red]")
#     except Exception as e:
#         print(f"[red]Failed to import links from JSON file: {e}[/red]")
