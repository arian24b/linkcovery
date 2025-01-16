#!/usr/bin/env python3

from typer import Option, Exit, prompt
from typing import List, Optional
from rich import print
from datetime import datetime
from os import path

from main import app
from database import LinkDatabase, User, Link
from importer import check_file, import_txt, import_csv


# Initialize database with settings
db = LinkDatabase()
db.get_connection()


# User Commands
@app.command("user-add", help="Add a new user to the database.")
def add_user(
    name: str = Option(..., prompt=True, help="Name of the user."),
    email: str = Option(..., prompt=True, help="Email of the user."),
) -> None:
    """
    Add a new user to the database.
    """
    user = User(
        id=None,
        name=name,
        email=email,
    )

    if user_id := db.create_user(user):
        print(f"[green]User '{name}' added with ID: {user_id}[/green]")
    else:
        print(f"[red]Failed to add user '{name}'.[/red]")


@app.command("user-list", help="List all users.")
def list_users() -> None:
    """
    List all users.
    """
    if not (users := db.read_users()):
        print("[yellow]No users found.[/yellow]")
        return None
    for user in users:
        print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")


# Link Commands
@app.command("link-add", help="Add a new link to the database.")
def add_link(
    url: str | None = Option(None, help="URL of the link."),
    domain: str | None = Option(None, help="Domain of the link."),
    author_email: str | None = Option(None, help="Email of the author."),
    description: str | None = Option("", help="Description of the link."),
    tags: list[str] = Option([], "--tag", "-t", help="Tags associated with the link."),
) -> None:
    """
    Add a new link to the database.
    """
    # Interactive prompts if arguments are not provided
    if not url:
        url = prompt("URL of the link")
    if not domain:
        domain = prompt("Domain of the link")
    if not author_email:
        author_email = prompt("Author's email")

    user = db.get_user_by_email(author_email)
    if not user:
        print(f"[red]Author with email '{author_email}' does not exist.[/red]")
        raise Exit(code=1)

    link = Link(
        id=None,
        url=url,
        domain=domain,
        description=description,
        tag=tags,
        author_id=user.id,
    )

    if link_id := db.create_link(link):
        print(f"[green]Link added with ID: {link_id}[/green]")
    else:
        print("[red]Failed to add link.[/red]")


@app.command("link-list", help="List all links with their authors.")
def list_links() -> None:
    """
    List all links with their authors.
    """
    links_with_authors = db.read_links_with_authors()
    if not links_with_authors:
        print("[yellow]No links found.[/yellow]")
        return None
    for entry in links_with_authors:
        link: Link = entry["link"]
        author = entry["author"]
        print(f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, Author: {author['name']} ({author['email']})")


@app.command("link-search", help="Search for links based on domain, tags, or description.")
def search_links(
    domain: str | None = Option(None, help="Filter by domain."),
    tags: list[str] = Option([], "--tag", "-t", help="Tags to filter by."),
    description: str | None = Option(None, help="Filter by description."),
    sort_by: str = Option("created_at", help="Field to sort by."),
    sort_order: str = Option("ASC", help="Sort order: ASC or DESC."),
    limit: int = Option(3, help="Number of results to return."),
    offset: int = Option(0, help="Number of results to skip."),
) -> None:
    """
    Search for links based on domain, tags, or description.
    """
    results = db.search_links(
        domain=domain,
        tags=tags,
        description=description,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    if not results:
        print("[yellow]No matching links found.[/yellow]")
        return None
    for link in results:
        print(
            f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, Description: {link.description}, Tags: {', '.join(link.tag)}"
        )


@app.command("link-delete", help="Delete a link by its ID.")
def delete_link(link_id: int = Option(..., help="ID of the link to delete.")) -> None:
    """
    Delete a link by its ID.
    """
    if db.delete_link(link_id):
        print(f"[green]Link with ID {link_id} has been deleted.[/green]")
    else:
        print(f"[red]Failed to delete link with ID {link_id}.[/red]")


@app.command("link-update", help="Update a link's details by its ID.")
def update_link(
    link_id: int = Option(..., help="ID of the link to update."),
    url: Optional[str] = Option(None, help="New URL of the link."),
    domain: Optional[str] = Option(None, help="New domain of the link."),
    description: Optional[str] = Option(None, help="New description of the link."),
    tags: Optional[List[str]] = Option(None, "--tag", "-t", help="New tags for the link."),
    is_read: Optional[bool] = Option(None, help="Mark as read or unread."),
) -> None:
    """
    Update a link's details by its ID.
    """
    existing_link = db.read_link(link_id)
    if not existing_link:
        print(f"[red]No link found with ID {link_id}.[/red]")
        raise Exit(code=1)

    # Interactive prompts for missing optional arguments
    if url is None and domain is None and description is None and tags is None and is_read is None:
        print("[yellow]No updates provided. Use options to specify fields to update.[/yellow]")
        raise Exit()

    # Update fields if new values are provided
    if url:
        existing_link.url = url
    if domain:
        existing_link.domain = domain
    if description is not None:
        existing_link.description = description
    if tags is not None:
        existing_link.tag = tags
    if is_read is not None:
        existing_link.is_read = is_read

    existing_link.updated_at = datetime.utcnow().isoformat()

    if db.update_link(link_id, existing_link):
        print(f"[green]Link with ID {link_id} has been updated.[/green]")
    else:
        print(f"[red]Failed to update link with ID {link_id}.[/red]")


# Import Commands
@app.command("import", help="Import links from a TXT or CSV file.")
def import_links(
    file_path: str = Option(..., help="Path to the .txt or .csv file to import."),
    author_id: int = Option(..., help="ID of the author to associate with the imported links."),
) -> None:
    """
    Import links from a TXT or CSV file into the database.
    """
    try:
        # Validate file
        if check_file(file_path):
            extension = path.splitext(file_path)[1].lower()
            try:
                if extension == ".txt":
                    import_txt(file_path, author_id, db)
                elif extension == ".csv":
                    import_csv(file_path, author_id, db)
                else:
                    print(f"[red]Unsupported file extension: {extension}[/red]")
            except Exception as e:
                print(f"[red]Import failed: {e}[/red]")
    except FileNotFoundError as fnf_error:
        print(f"[red]{fnf_error}[/red]")
        raise Exit(code=1)
    except ValueError as val_error:
        print(f"[red]{val_error}[/red]")
        raise Exit(code=1)
    except Exception as e:
        print(f"[red]An unexpected error occurred: {e}[/red]")
        raise Exit(code=1)


if __name__ == "__main__":
    app()
