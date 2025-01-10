#!/usr/bin/env python3

from typer import Typer, Option, Exit
from typing import List, Optional
from rich import print
from datetime import datetime

from database import LinkDatabase, User, Link

app = Typer(help="Linkcovery CLI Application")

db = LinkDatabase()
db.connect()


@app.command()
def add_user(name: str, email: str):
    """
    Add a new user to the database.
    """
    user = User(name=name, email=email)
    user_id = db.create_user(user)
    if user_id:
        print(f"[green]User '{name}' added with ID: {user_id}[/green]")
    else:
        print(f"[red]Failed to add user '{name}'.[/red]")


@app.command()
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


@app.command()
def add_link(
    url: str,
    domain: str,
    author_email: str,
    description: Optional[str] = "",
    tags: List[str] = Option([], "--tag", "-t", help="Tags associated with the link."),
):
    """
    Add a new link to the database.
    """
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


@app.command()
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


@app.command()
def search_links(
    domain: Optional[str] = None,
    tags: List[str] = Option([], "--tag", "-t", help="Tags to filter by."),
    description: Optional[str] = None,
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


@app.command()
def delete_link(link_id: int):
    """
    Delete a link by its ID.
    """
    db.delete_link(link_id)


@app.command()
def update_link(
    link_id: int,
    url: Optional[str] = None,
    domain: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = Option(None, "--tag", "-t", help="Tags to update."),
    is_read: Optional[bool] = None,
):
    """
    Update a link's details by its ID.
    """
    existing_link = db.read_link(link_id)
    if not existing_link:
        print(f"[red]No link found with ID {link_id}.[/red]")
        raise Exit(code=1)

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
