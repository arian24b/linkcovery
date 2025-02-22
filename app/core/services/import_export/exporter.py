from csv import DictWriter
from json import dump
from rich.progress import track

from app.core.database import link_service, user_service
from app.core.logger import AppLogger

logger = AppLogger(__name__)


def export_users_to_json(output_path: str) -> None:
    users = user_service.get_users()
    users_data = []
    for user in users:
        users_data.append({col: getattr(user, col) for col in user.__table__.columns.keys()})
    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            dump(users_data, json_file, indent=4)
        logger.info(f"Successfully exported {len(users)} users to {output_path}.")
    except Exception as e:
        logger.error(f"Failed to export users to JSON: {e}")


def export_users_to_csv(output_path: str) -> None:
    users = user_service.get_users()
    if not users:
        logger.warning("No users available to export.")
        return

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
            fieldnames = list(users[0].__table__.columns.keys())
            writer = DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for user in track(users, description="Exporting users..."):
                row = {col: getattr(user, col) for col in fieldnames}
                writer.writerow(row)
        logger.info(f"Successfully exported {len(users)} users to {output_path}.")
    except Exception as e:
        logger.error(f"Failed to export users to CSV: {e}")


def export_links_to_json(output_path: str, author_id: int | None = None) -> None:
    if author_id is not None:
        links = link_service.get_links_by_author(author_id)
    else:
        links = link_service.get_links()
    links_data = []
    for link in links:
        link_data = {col: getattr(link, col) for col in link.__table__.columns.keys()}
        if link.author:
            link_data["author"] = {col: getattr(link.author, col) for col in link.author.__table__.columns.keys()}
        links_data.append(link_data)
    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            dump(links_data, json_file, indent=4)
        logger.info(f"Successfully exported {len(links_data)} links to {output_path}.")
    except Exception as e:
        logger.error(f"Failed to export links to JSON: {e}")


def export_links_to_csv(output_path: str, author_id: int | None = None) -> None:
    if author_id is not None:
        links = link_service.get_links_by_author(author_id)
    else:
        links = link_service.get_links()
    if not links:
        logger.warning("No links available to export.")
        return

    headers = list(links[0].__table__.columns.keys()) + ["author_name", "author_email"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for link in track(links, description="Exporting links..."):
                row = {col: getattr(link, col) for col in link.__table__.columns.keys()}
                if link.author:
                    row["author_name"] = link.author.name
                    row["author_email"] = link.author.email
                else:
                    row["author_name"] = ""
                    row["author_email"] = ""
                writer.writerow(row)
        logger.info(f"Successfully exported {len(links)} links to {output_path}.")
    except Exception as e:
        logger.error(f"Failed to export links to CSV: {e}")
