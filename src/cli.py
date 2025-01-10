#!/usr/bin/env python3

from typer import Typer, Option, Exit, prompt
from typing import List, Optional
from rich import print
from datetime import datetime

from database import LinkDatabase, User, Link
from settings import settings  # noqa

app = Typer(help="Linkcovery CLI Application")

# Create sub-applications for users and links
user_app = Typer(help="User management commands.")
link_app = Typer(help="Link management commands.")

# Add sub-applications to the main app
app.add_typer(user_app, name="user", help="Manage users.")
app.add_typer(link_app, name="link", help="Manage links.")

# Initialize database with settings
db = LinkDatabase()
db.connect()


@user_app.command("add")
def add_user(
    name: str = Option(..., prompt=True, help="Name of the user."),
    email: str = Option(..., prompt=True, help="Email of the user."),
):
    """
    Add a new user to the database.
    """
    user = User(name=name, email=email)
    user_id = db.create_user(user)
    if user_id:
        print(f"[green]User '{name}' added with ID: {user_id}[/green]")
    else:
        print(f"[red]Failed to add user '{name}'.[/red]")


@user_app.command("list")
def list_users():
    """
    List all users.
    """
    users = db.read_users()
    if not users:
        print("[yellow]No users found.[/yellow]")
        return
    for user in users:
        print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")


@link_app.command("add")
def add_link(
    url: Optional[str] = Option(None, help="URL of the link."),
    domain: Optional[str] = Option(None, help="Domain of the link."),
    author_email: Optional[str] = Option(None, help="Email of the author."),
    description: Optional[str] = Option("", help="Description of the link."),
    tags: List[str] = Option([], "--tag", "-t", help="Tags associated with the link."),
):
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
        url=url,
        domain=domain,
        description=description,
        tag=tags,
        author_id=user.id,
    )
    db.create_link(link)


@link_app.command("list")
def list_links():
    """
    List all links with their authors.
    """
    links_with_authors = db.read_links_with_authors()
    if not links_with_authors:
        print("[yellow]No links found.[/yellow]")
        return
    for entry in links_with_authors:
        link: Link = entry["link"]
        author = entry["author"]
        print(f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, Author: {author['name']} ({author['email']})")


@link_app.command("search")
def search_links(
    domain: Optional[str] = Option(None, help="Filter by domain."),
    tags: List[str] = Option([], "--tag", "-t", help="Tags to filter by."),
    description: Optional[str] = Option(None, help="Filter by description."),
    sort_by: str = Option("created_at", help="Field to sort by."),
    sort_order: str = Option("ASC", help="Sort order: ASC or DESC."),
    limit: int = Option(10, help="Number of results to return."),
    offset: int = Option(0, help="Number of results to skip."),
):
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
        return
    for link in results:
        print(
            f"ID: {link.id}, URL: {link.url}, Domain: {link.domain}, Description: {link.description}, Tags: {', '.join(link.tag)}"
        )


@link_app.command("delete")
def delete_link(link_id: int = Option(..., help="ID of the link to delete.")):
    """
    Delete a link by its ID.
    """
    db.delete_link(link_id)


@link_app.command("update")
def update_link(
    link_id: int = Option(..., help="ID of the link to update."),
    url: Optional[str] = Option(None, help="New URL of the link."),
    domain: Optional[str] = Option(None, help="New domain of the link."),
    description: Optional[str] = Option(None, help="New description of the link."),
    tags: Optional[List[str]] = Option(None, "--tag", "-t", help="New tags for the link."),
    is_read: Optional[bool] = Option(None, help="Mark as read or unread."),
):
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

    db.update_link(link_id, existing_link)


@app.callback()
def main():
    """
    Linkcovery CLI allows you to manage users and links.
    """
    pass


if __name__ == "__main__":
    app()
