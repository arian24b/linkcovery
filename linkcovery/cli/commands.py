"""Simple CLI commands for LinKCovery."""

import typer
from rich import print
from typer import Option

from linkcovery.core.config import config

app = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=True,
    help="LinKCovery - Simple bookmark management",
)


@app.command()
def add(
    url: str = Option(..., help="URL to add"),
    description: str = Option("", "--desc", "-d", help="Description"),
    tag: str = Option("", "--tag", "-t", help="Tag"),
    read: bool = Option(False, "--read", "-r", help="Mark as read"),
) -> None:
    """Add a new link."""
    try:
        from linkcovery.core.database import get_database

        db = get_database()
        link = db.add_link(url, description, tag, read)
        print(f"✅ Added link #{link.id}: {url}")
        if description:
            print(f"   Description: {description}")
        if tag:
            print(f"   Tag: {tag}")
    except Exception as e:
        print(f"❌ Error: {e}")


@app.command()
def list() -> None:
    """List all links."""
    try:
        from linkcovery.core.database import get_database

        db = get_database()
        links = db.get_all_links()

        if not links:
            print("📭 No links found")
            return

        print(f"📚 {len(links)} links:")
        for link in links:
            status = "✅" if link.is_read else "⏳"
            print(f"{link.id:3}. {status} {link.url}")
            if link.description:
                print(f"     📝 {link.description}")
            if link.tag:
                print(f"     🏷️  {link.tag}")
            print(f"     📅 {link.created_at[:10]}")
    except Exception as e:
        print(f"❌ Error: {e}")


@app.command()
def search(
    query: str = Option("", help="Search in URL, description, or tags"),
    domain: str = Option("", help="Filter by domain"),
    tag: str = Option("", help="Filter by tag"),
    read: bool = Option(False, "--read-only", help="Show only read links"),
    unread: bool = Option(False, "--unread-only", help="Show only unread links"),
    limit: int = Option(10, help="Max results"),
) -> None:
    """Search links."""
    try:
        from linkcovery.core.database import get_database

        db = get_database()

        # Determine read status filter
        is_read = None
        if read:
            is_read = True
        elif unread:
            is_read = False

        results = db.search_links(query, domain, tag, is_read, limit)

        if not results:
            print("🔍 No matches found")
            return

        print(f"🔍 Found {len(results)} matches:")
        for link in results:
            status = "✅" if link.is_read else "⏳"
            print(f"{link.id:3}. {status} {link.url}")
            if link.description:
                print(f"     📝 {link.description}")
            if link.tag:
                print(f"     🏷️  {link.tag}")
    except Exception as e:
        print(f"❌ Error: {e}")


@app.command()
def show(link_id: int = Option(..., help="Link ID")) -> None:
    """Show link details."""
    try:
        from linkcovery.core.database import get_database

        db = get_database()
        link = db.get_link(link_id)

        if not link:
            print(f"❌ Link #{link_id} not found")
            return

        status = "✅ Read" if link.is_read else "⏳ Unread"
        print(f"📖 Link #{link.id}")
        print(f"   URL: {link.url}")
        print(f"   Domain: {link.domain}")
        print(f"   Description: {link.description or 'None'}")
        print(f"   Tags: {link.tag or 'None'}")
        print(f"   Status: {status}")
        print(f"   Created: {link.created_at}")
        print(f"   Updated: {link.updated_at}")
    except Exception as e:
        print(f"❌ Error: {e}")


@app.command()
def update(
    link_id: int = Option(..., help="Link ID"),
    url: str = Option(None, help="New URL"),
    description: str = Option(None, "--desc", "-d", help="New description"),
    tag: str = Option(None, "--tag", "-t", help="New tag"),
    read: bool = Option(False, "--read", help="Mark as read"),
    unread: bool = Option(False, "--unread", help="Mark as unread"),
) -> None:
    """Update a link."""
    try:
        from linkcovery.core.database import get_database

        db = get_database()

        updates = {}
        if url:
            updates["url"] = url
        if description is not None:
            updates["description"] = description
        if tag is not None:
            updates["tag"] = tag
        if read:
            updates["is_read"] = True
        elif unread:
            updates["is_read"] = False

        if not updates:
            print("⚠️  No changes specified")
            return

        db.update_link(link_id, **updates)
        print(f"✅ Updated link #{link_id}")
    except Exception as e:
        print(f"❌ Error: {e}")


@app.command()
def delete(link_id: int = Option(..., help="Link ID")) -> None:
    """Delete a link."""
    try:
        from linkcovery.core.database import get_database

        db = get_database()

        link = db.get_link(link_id)
        if not link:
            print(f"❌ Link #{link_id} not found")
            return

        db.delete_link(link_id)
        print(f"✅ Deleted: {link.url}")
    except Exception as e:
        print(f"❌ Error: {e}")


@app.command()
def export(filename: str = Option("links.json", help="Output file")) -> None:
    """Export links to JSON."""
    try:
        from linkcovery.core.utils import export_links_to_json

        export_links_to_json(filename)
    except Exception as e:
        print(f"❌ Error: {e}")


@app.command(name="import")
def import_links(filename: str = Option(..., help="JSON file to import")) -> None:
    """Import links from JSON."""
    try:
        from linkcovery.core.utils import import_links_from_json

        import_links_from_json(filename)
    except Exception as e:
        print(f"❌ Error: {e}")


@app.command()
def stats() -> None:
    """Show statistics."""
    try:
        from linkcovery.core.database import get_database

        db = get_database()
        links = db.get_all_links()

        if not links:
            print("📭 No links yet")
            return

        read_count = sum(1 for link in links if link.is_read)
        unread_count = len(links) - read_count

        # Count domains
        domains = {}
        for link in links:
            domains[link.domain] = domains.get(link.domain, 0) + 1

        print("📊 Statistics:")
        print(f"   Total links: {len(links)}")
        print(f"   Read: {read_count}")
        print(f"   Unread: {unread_count}")
        print("   Top domains:")

        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"     {domain}: {count}")
    except Exception as e:
        print(f"❌ Error: {e}")


@app.command()
def version() -> None:
    """Show version information."""
    print(f"{config.APP_NAME} v{config.VERSION}")


# For backwards compatibility
def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        print(f"{config.APP_NAME} v{config.VERSION}")
        raise typer.Exit


if __name__ == "__main__":
    app()
