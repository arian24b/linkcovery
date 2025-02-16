from csv import DictWriter
from json import dump
from rich.progress import track
from pathlib import Path

from app.core.models import LinkDatabase, User, Link
from app.core.logger import AppLogger

logger = AppLogger(__name__)


def export_users_to_json(db: LinkDatabase, output_path: str) -> None:
    """
    Exports all users to a JSON file.

    Args:
        db (LinkDatabase): The database instance.
        output_path (str): Path to the output JSON file.
    """
    users: list[User] = db.read_users()
    users_data = [user.model_dump() for user in users]

    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            dump(users_data, json_file, indent=4)
        logger.info(f"Successfully exported {len(users)} users to {output_path}.")
    except Exception as e:
        logger.error(f"Failed to export users to JSON: {e}")


def export_users_to_csv(db: LinkDatabase, output_path: str) -> None:
    """
    Exports all users to a CSV file.

    Args:
        db (LinkDatabase): The database instance.
        output_path (str): Path to the output CSV file.
    """
    users: list[User] = db.read_users()
    if not users:
        logger.warning("No users available to export.")
        return

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = DictWriter(csv_file, fieldnames=users[0].model_dump().keys())
            writer.writeheader()
            for user in track(users, description="Exporting users..."):
                writer.writerow(user.dict())
        logger.info(f"Successfully exported {len(users)} users to {output_path}.")
    except Exception as e:
        logger.error(f"Failed to export users to CSV: {e}")


def export_links_to_json(db: LinkDatabase, output_path: str) -> None:
    """
    Exports all links to a JSON file.

    Args:
        db (LinkDatabase): The database instance.
        output_path (str): Path to the output JSON file.
    """
    links_with_authors = db.read_links_with_authors()
    links_data = []
    for entry in links_with_authors:
        link = entry["link"].dict()
        link["author"] = entry["author"]
        links_data.append(link)

    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            dump(links_data, json_file, indent=4)
        logger.info(f"Successfully exported {len(links_data)} links to {output_path}.")
    except Exception as e:
        logger.error(f"Failed to export links to JSON: {e}")


def export_links_to_csv(db: LinkDatabase, output_path: str) -> None:
    """
    Exports all links to a CSV file.

    Args:
        db (LinkDatabase): The database instance.
        output_path (str): Path to the output CSV file.
    """
    links_with_authors = db.read_links_with_authors()
    if not links_with_authors:
        logger.warning("No links available to export.")
        return

    headers = [
        "id",
        "url",
        "domain",
        "description",
        "tag",
        "author_id",
        "is_read",
        "created_at",
        "updated_at",
        "author_name",
        "author_email",
    ]

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for entry in track(links_with_authors, description="Exporting links..."):
                link: Link = entry["link"]
                author = entry["author"]
                row = link.model_dump()
                row["tag"] = ", ".join(link.tag)
                row["author_name"] = author["name"]
                row["author_email"] = author["email"]
                writer.writerow(row)
        logger.info(f"Successfully exported {len(links_with_authors)} links to {output_path}.")
    except Exception as e:
        logger.error(f"Failed to export links to CSV: {e}")


def export_all(db: LinkDatabase, format: str = "json", output_dir: str | None = None) -> None:
    """
    Exports both users and links to the specified format.

    Args:
        db (LinkDatabase): The database instance.
        format (str): Export format ('json' or 'csv').
        output_dir (Optional[str]): Directory to store exported files. Defaults to current directory.
    """
    format = format.lower()
    if format not in {"json", "csv"}:
        logger.error(f"Unsupported export format: {format}. Choose 'json' or 'csv'.")
        return

    if not output_dir:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    users_output = output_dir / f"users_export.{format}"
    links_output = output_dir / f"links_export.{format}"

    if format == "json":
        export_users_to_json(db, str(users_output))
        export_links_to_json(db, str(links_output))
    elif format == "csv":
        export_users_to_csv(db, str(users_output))
        export_links_to_csv(db, str(links_output))

    logger.info(f"Exported all data successfully to '{users_output}' and '{links_output}'.")
