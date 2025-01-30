from os import path
from rich import print
from pydantic import HttpUrl, ValidationError
from urllib.parse import urlparse
from csv import DictReader
from json import JSONDecodeError, load

from settings import settings
from database import LinkDatabase, User, Link


def check_file(file_path: str) -> bool:
    """
    Validates the existence and extension of the provided file.

    Args:
        file_path (str): Path to the file to be checked.

    Returns:
        bool: True if the file exists and has a valid extension.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension is not allowed.
    """
    if not path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = path.splitext(file_path)[1].lower()
    if extension not in {f".{ext}" for ext in settings.ALLOW_EXTENSIONS}:
        raise ValueError(f"Invalid file extension: {extension}. Allowed extensions: {settings.ALLOW_EXTENSIONS}")

    return True


def extract_domain(url: str) -> str:
    """
    Extracts the domain from a given URL.

    Args:
        url (str): The URL from which to extract the domain.

    Returns:
        str: The domain of the URL.
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc


def parse_tags(domain: str) -> list[str]:
    """
    Generates tags based on the domain.

    Args:
        domain (str): The domain to generate tags from.

    Returns:
        List[str]: A list of tags.
    """
    return domain.split(".")


def import_txt(file_path: str, author_id: int, db: LinkDatabase):
    """
    Imports links from a .txt file. Each line in the file should contain one URL.

    Args:
        file_path (str): Path to the .txt file.
        author_id (int): ID of the author to associate with the imported links.
        db (LinkDatabase): Instance of the database connection.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as txtfile:
            links = [line.strip() for line in txtfile if line.strip()]

        if not links:
            print("[yellow]No links found in the TXT file.[/yellow]")
            return

        with db.transaction():
            for line_number, link in enumerate(links, start=1):
                try:
                    url = HttpUrl(link)
                    domain = extract_domain(str(url))
                    tags = parse_tags(domain)
                    link_obj = Link(
                        id=None,
                        url=url,
                        domain=domain,
                        description="Imported from TXT",
                        tag=tags,
                        author_id=author_id,
                    )
                    link_id = db.create_link(link_obj)
                    if link_id:
                        print(f"[green]Line {line_number}: Link imported with ID {link_id}.[/green]")
                except ValidationError as ve:
                    print(f"[red]Line {line_number}: Invalid URL '{link}'. Error: {ve}[/red]")
                    raise  # Trigger transaction rollback
                except Exception as e:
                    print(f"[red]Line {line_number}: Failed to import link '{link}'. Error: {e}[/red]")
                    raise  # Trigger transaction rollback

        print("[green]All links from TXT file have been imported successfully.[/green]")
    except Exception as e:
        print(f"[red]Failed to import from TXT file: {e}[/red]")


def import_csv(file_path: str, author_id: int, db: LinkDatabase):
    """
    Imports links from a .csv file. The CSV should have headers corresponding to Link fields.

    Expected CSV Headers:
    - url
    - domain
    - description
    - tag (comma-separated if multiple)
    - is_read

    Args:
        file_path (str): Path to the .csv file.
        author_id (int): ID of the author to associate with the imported links.
        db (LinkDatabase): Instance of the database connection.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as csvfile:
            reader = DictReader(csvfile)
            required_fields = {"url", "domain", "description", "tag", "is_read"}
            if not required_fields.issubset(reader.fieldnames):
                print(f"[red]CSV file is missing required fields. Required fields: {required_fields}[/red]")
                return

            links = list(reader)
            if not links:
                print("[yellow]No links found in the CSV file.[/yellow]")
                return

            with db.transaction():
                for row_number, row in enumerate(links, start=2):  # Start at 2 considering header
                    try:
                        url = HttpUrl(row["url"])
                        domain = row["domain"] or extract_domain(str(url))
                        tags = [tag.strip() for tag in row["tag"].split(",")] if row["tag"] else []
                        is_read = row.get("is_read", "False").strip().lower() in {"1", "true", "yes"}

                        link_obj = Link(
                            id=None,
                            url=url,
                            domain=domain,
                            description=row.get("description", "Imported from CSV"),
                            tag=tags,
                            author_id=author_id,
                            is_read=is_read,
                        )
                        link_id = db.create_link(link_obj)
                        if link_id:
                            print(f"[green]Row {row_number}: Link imported with ID {link_id}.[/green]")
                    except ValidationError as ve:
                        print(f"[red]Row {row_number}: Invalid data. Error: {ve}[/red]")
                        raise  # Trigger transaction rollback
                    except Exception as e:
                        print(f"[red]Row {row_number}: Failed to import link. Error: {e}[/red]")
                        raise  # Trigger transaction rollback

        print("[green]All links from CSV file have been imported successfully.[/green]")
    except Exception as e:
        print(f"[red]Failed to import from CSV file: {e}[/red]")


def import_links_from_json(file_path: str, db: LinkDatabase):
    """
    Imports links from a JSON file.

    Args:
        file_path (str): Path to the JSON file.
        db (LinkDatabase): Instance of the database connection.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            links_data = load(json_file)

        if not links_data:
            print("[yellow]No links found in the JSON file.[/yellow]")
            return

        new_links = []
        for index, link_dict in enumerate(links_data, start=1):
            try:
                # Extract author_email to find or create the user
                author_info = link_dict.pop("author", {})
                author_email = author_info.get("email")
                if not author_email:
                    print(f"[red]Link {index}: Missing author email. Skipping.[/red]")
                    continue

                user = db.get_user_by_email(author_email)
                if not user:
                    # Optionally, create the user if they don't exist
                    user = User(name=author_info.get("name", "Unknown"), email=author_email)
                    user_id = db.create_user(user)
                    if not user_id:
                        print(f"[red]Link {index}: Failed to create user '{author_email}'. Skipping link.[/red]")
                        continue
                    user.id = user_id

                # Prepare Link object
                link_obj = Link(**link_dict)
                link_obj.author_id = user.id

                # Check if link already exists
                existing_link = db.read_link_by_url(link_obj.url)
                if existing_link:
                    print(f"[yellow]Link with URL '{link_obj.url}' already exists. Skipping.[/yellow]")
                    continue

                new_links.append(link_obj)
            except ValidationError as ve:
                print(f"[red]Link {index}: Validation error: {ve}[/red]")
                raise  # Trigger transaction rollback
            except Exception as e:
                print(f"[red]Link {index}: Failed to prepare link. Error: {e}[/red]")
                raise  # Trigger transaction rollback

        if new_links:
            db.bulk_create_links(new_links)
            print(f"[green]Successfully imported {len(new_links)} links from JSON file.[/green]")
        else:
            print("[yellow]No new links to import.[/yellow]")

    except JSONDecodeError as jde:
        print(f"[red]Invalid JSON format: {jde}[/red]")
    except Exception as e:
        print(f"[red]Failed to import links from JSON file: {e}[/red]")
