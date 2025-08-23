"""Link management commands for LinKCovery CLI."""

import asyncio

import typer
from rich.table import Table

from linkcovery.core.utils import confirm_action, console, fetch_description_and_tags, handle_errors
from linkcovery.services import get_link_service

app = typer.Typer(help="Manage your bookmarked links", no_args_is_help=True)


@app.command()
@handle_errors
def add(
    url: str = typer.Argument(..., help="URL to bookmark"),
    description: str = typer.Option("", "--desc", "-d", help="Description for the link"),
    tag: str = typer.Option("", "--tag", "-t", help="Tag to categorize the link"),
    read: bool = typer.Option(False, "--read", "-r", help="Mark as already read"),
    no_fetch: bool = typer.Option(False, "--no-fetch", help="Skip fetching metadata from URL"),
) -> None:
    """Add a new link to your bookmarks."""
    link_service = get_link_service()

    # Only fetch metadata if not provided and not explicitly disabled
    if not no_fetch and not (description and tag):
        try:
            fetch = asyncio.run(fetch_description_and_tags(url=url))
            final_description = description or fetch["description"]
            final_tag = tag or fetch["tags"]
        except Exception:
            # If fetching fails, continue with provided or empty values
            final_description = description
            final_tag = tag
    else:
        final_description = description
        final_tag = tag

    link = link_service.add_link(
        url=url,
        description=final_description,
        tag=final_tag,
        is_read=read,
    )

    console.print(f"✅ Added link #{link.id}", style="green")
    console.print(f"   URL: {url}")
    if final_description:
        console.print(f"   Description: {final_description}")
    if final_tag:
        console.print(f"   Tag: {final_tag}")
    if read:
        console.print("   Status: Read")


@app.command(name="list")
@handle_errors
def list_links(
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of links to show"),
    read_only: bool = typer.Option(False, "--read-only", help="Show only read links"),
    unread_only: bool = typer.Option(False, "--unread-only", help="Show only unread links"),
) -> None:
    """List your bookmarked links."""
    link_service = get_link_service()

    # Determine read status filter
    is_read = None
    if read_only:
        is_read = True
    elif unread_only:
        is_read = False

    # Get links with filter
    if is_read is not None:
        links = link_service.search_links(is_read=is_read, limit=limit)
    else:
        links = link_service.list_all_links()
        if limit and len(links) > limit:
            links = links[:limit]

    if not links:
        console.print("📭 No links found", style="yellow")
        return

    # Create table
    table = Table(title=f"📚 Your Links ({len(links)} shown)")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Status", width=6)
    table.add_column("URL", style="blue")
    table.add_column("Description", style="dim")
    table.add_column("Tag", style="magenta")
    table.add_column("Added", style="dim", width=10)

    for link in links:
        status = "✅ Read" if link.is_read else "⏳ New"
        desc = link.description[:50] + "..." if len(link.description) > 50 else link.description
        tag = link.tag or ""
        date = link.created_at[:10] if link.created_at else ""

        table.add_row(str(link.id), status, link.url, desc, tag, date)

    console.print(table)


@app.command()
@handle_errors
def search(
    query: str = typer.Argument("", help="Search in URLs, descriptions, and tags"),
    domain: str = typer.Option("", "--domain", help="Filter by domain"),
    tag: str = typer.Option("", "--tag", "-t", help="Filter by tag"),
    read_only: bool = typer.Option(False, "--read-only", help="Show only read links"),
    unread_only: bool = typer.Option(False, "--unread-only", help="Show only unread links"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum results"),
) -> None:
    """Search your bookmarks."""
    link_service = get_link_service()

    # Determine read status filter
    is_read = None
    if read_only:
        is_read = True
    elif unread_only:
        is_read = False

    results = link_service.search_links(
        query=query,
        domain=domain,
        tag=tag,
        is_read=is_read,
        limit=limit,
    )

    if not results:
        console.print("🔍 No matches found", style="yellow")
        return

    # Create table
    table = Table(title=f"🔍 Search Results ({len(results)} found)")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Status", width=6)
    table.add_column("URL", style="blue")
    table.add_column("Description", style="dim")
    table.add_column("Tag", style="magenta")

    for link in results:
        status = "✅" if link.is_read else "⏳"
        desc = link.description[:50] + "..." if len(link.description) > 50 else link.description
        tag = link.tag or ""

        table.add_row(str(link.id), status, link.url, desc, tag)

    console.print(table)


@app.command()
@handle_errors
def show(link_id: int = typer.Argument(..., help="Link ID to display")) -> None:
    """Show detailed information about a specific link."""
    link_service = get_link_service()
    link = link_service.get_link(link_id)

    console.print(f"📖 Link #{link.id}", style="bold blue")
    console.print(f"   URL: {link.url}")
    console.print(f"   Domain: {link.domain}")
    console.print(f"   Description: {link.description or 'None'}")
    console.print(f"   Tag: {link.tag or 'None'}")
    console.print(f"   Status: {'✅ Read' if link.is_read else '⏳ Unread'}")
    console.print(f"   Created: {link.created_at}")
    console.print(f"   Updated: {link.updated_at}")


@app.command()
@handle_errors
def edit(
    link_id: int = typer.Argument(..., help="Link ID to edit"),
    url: str | None = typer.Option(None, "--url", help="New URL"),
    description: str | None = typer.Option(None, "--desc", "-d", help="New description"),
    tag: str | None = typer.Option(None, "--tag", "-t", help="New tag"),
    read: bool = typer.Option(False, "--read", "-r", help="Mark as read"),
    unread: bool = typer.Option(False, "--unread", "-u", help="Mark as unread"),
) -> None:
    """Edit an existing link."""
    link_service = get_link_service()

    # Determine read status
    is_read = None
    if read:
        is_read = True
    elif unread:
        is_read = False

    # Check if any updates were provided
    if not any([url, description is not None, tag is not None, is_read is not None]):
        console.print("⚠️ No updates specified", style="yellow")
        return

    link = link_service.update_link(
        link_id=link_id,
        url=url,
        description=description,
        tag=tag,
        is_read=is_read,
    )

    console.print(f"✅ Updated link #{link.id}", style="green")


@app.command()
@handle_errors
def delete(
    link_id: list[int] = typer.Argument(..., help="Link ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a link from your bookmarks."""
    link_service = get_link_service()

    # Get link details for confirmation
    links = [link_service.get_link(id) for id in link_id]

    if not force and not confirm_action(f"Delete links: {', '.join(str(link.id) for link in links)}?"):
        console.print("🛑 Deletion cancelled", style="yellow")
        return

    for link in links:
        link_service.delete_link(link.id)
    console.print(f"✅ Deleted links: {', '.join(str(link.id) for link in links)}", style="green")


@app.command("mark-read")
@handle_errors
def mark_read(link_id: list[int] = typer.Argument(..., help="Link ID to mark as read")) -> None:
    """Mark a link as read."""
    link_service = get_link_service()
    for id in link_id:
        link = link_service.mark_as_read(id)
        console.print(f"✅ Marked link #{link.id} as read", style="green")


@app.command("mark-unread")
@handle_errors
def mark_unread(link_id: list[int] = typer.Argument(..., help="Link ID to mark as unread")) -> None:
    """Mark a link as unread."""
    link_service = get_link_service()
    for id in link_id:
        link = link_service.mark_as_unread(id)
        console.print(f"✅ Marked link #{link.id} as unread", style="green")


@app.command()
@handle_errors
def normalize(
    link_id: list[int] = typer.Argument(None, help="Link IDs to normalize"),
    all_links: bool = typer.Option(False, "--all", "-a", help="Normalize all links"),
) -> None:
    """Normalize link URLs by removing trailing slashes, converting http to https, and removing www."""
    link_service = get_link_service()

    if all_links:
        # Normalize all links
        if link_id:
            console.print("⚠️ Ignoring specific link IDs when --all is used", style="yellow")

        console.print("🔄 Normalizing all links...", style="blue")

        if normalized_links := link_service.normalize_all_links():
            console.print(f"✅ Normalized {len(normalized_links)} links", style="green")
            for link in normalized_links:
                console.print(f"   • Link #{link.id}: {link.url}", style="dim")
        else:
            console.print("📭 No links found to normalize", style="yellow")
    elif link_id:
        # Normalize specific links
        for id in link_id:
            try:
                link = link_service.normalize_link(id)
                console.print(f"✅ Normalized link #{link.id}: {link.url}", style="green")
            except Exception as e:
                console.print(f"❌ Failed to normalize link #{id}: {e}", style="red")
    else:
        console.print("⚠️ Please specify link IDs or use --all to normalize all links", style="yellow")


@app.command()
@handle_errors
def read_random(
    number: int = typer.Option(5, "--number", "-n", help="Number of random links to read"),
    include_read: bool = typer.Option(False, "--include-read", help="Include already read links"),
) -> None:
    """Read random links from your bookmarks and mark them as read."""
    link_service = get_link_service()

    if number < 1:
        console.print("⚠️ Number must be at least 1", style="yellow")
        return

    links = link_service.get_random_links(number=number, unread_only=not include_read)

    if not links:
        filter_msg = "unread " if not include_read else ""
        console.print(f"📭 No {filter_msg}links available to read", style="yellow")
        return

    console.print(f"📚 Reading {len(links)} random link{'s' if len(links) > 1 else ''}:", style="bold blue")

    for link in links:
        console.print(f"🔗 Reading link #{link.id}: {link.url}", style="blue")
        if link.description:
            console.print(f"   📝 {link.description}", style="dim")

        # Only mark as read if it wasn't already read
        if not link.is_read:
            link_service.mark_as_read(link.id)
            console.print("   ✅ Marked as read", style="green")
        else:
            console.print("   📖 Already read", style="dim")
        console.print()  # Add empty line for readability
