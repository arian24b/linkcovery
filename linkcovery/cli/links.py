"""Link management commands for LinkCovery CLI."""

import json
from asyncio import run as asyncio_run

import typer
from rich.table import Table

from linkcovery.cli.cli_state import state
from linkcovery.core.utils import confirm_action, console, err_console, fetch_description, handle_errors


def _link_service():
    from linkcovery.services.link_service import get_link_service

    return get_link_service()


app = typer.Typer(help="Manage your bookmarked links", no_args_is_help=True)


def _link_dict(link) -> dict:
    """Serializable representation of a link for --json output."""
    return {
        "id": link.id,
        "url": link.url,
        "domain": link.domain,
        "description": link.description,
        "tag": link.tag,
        "is_read": link.is_read,
        "created_at": link.created_at,
        "updated_at": link.updated_at,
    }


def _emit_json(payload) -> None:
    """Print a JSON payload to stdout (single source of truth for --json)."""
    console.print(json.dumps(payload, ensure_ascii=False, default=str))


@app.command(rich_help_panel="Link Management")
@handle_errors
def add(
    url: str = typer.Argument(..., help="URL to bookmark"),
    description: str = typer.Option("", "--desc", "-d", help="Description for link"),
    tag: str | None = typer.Option(None, "--tag", "-t", help="Tag to categorize link"),
    read: bool = typer.Option(False, "--read", "-r", help="Mark as already read"),
    no_fetch: bool = typer.Option(False, "--no-fetch", help="Skip fetching metadata from URL"),
    timeout: int = typer.Option(10, "--timeout", help="Timeout for fetching metadata (seconds)"),
) -> None:
    """Add a new link to your bookmarks.

    Examples:
        linkcovery add "https://github.com/arian24b/linkcovery"
        linkcovery add "url.com" --tag "python,cli" --desc "Great tool"
        linkcovery add "url.com" --read --no-fetch
        linkcovery add "url.com" --timeout 30

    """
    link_service = _link_service()

    link = link_service.add_link(
        url=url,
        description=description
        if description or no_fetch
        else asyncio_run(fetch_description(url=url, timeout=timeout, show_spinner=True)),
        tag=tag or "",
        is_read=read,
    )

    if state.json_mode:
        _emit_json(_link_dict(link))
        return

    console.print(f"✅ Added link #{link.id}", style="green")
    console.print(f"   URL: {url}")


@app.command(name="list", rich_help_panel="Link Management")
@handle_errors
def list_links(
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of links to show"),
    read_only: bool = typer.Option(False, "--read-only", help="Show only read links"),
    unread_only: bool = typer.Option(False, "--unread-only", help="Show only unread links"),
    full: bool = typer.Option(False, "--full", help="Show full descriptions without truncation"),
) -> None:
    """List your bookmarked links.

    Examples:
        linkcovery list
        linkcovery list --limit 10
        linkcovery list --unread-only
        linkcovery list --full

    """
    link_service = _link_service()

    is_read = None
    if read_only:
        is_read = True
    elif unread_only:
        is_read = False

    if is_read is not None:
        links = link_service.search_links(is_read=is_read, limit=limit)
    else:
        links = link_service.list_all_links()
        if limit and len(links) > limit:
            links = links[:limit]

    if state.json_mode:
        _emit_json([_link_dict(link) for link in links])
        return

    if not links:
        console.print("📭 No links found", style="yellow")
        return

    table = Table(
        title=f"📚 Your Links ({len(links)} shown)",
        show_lines=bool(full),
        box=None,
        header_style="dim",
    )
    table.add_column("ID", style="cyan", width=4, justify="right")
    table.add_column("Status", width=6)
    table.add_column("URL", style="blue")
    table.add_column("Description", style="dim")
    table.add_column("Tag", style="magenta")
    table.add_column("Added", style="dim", width=10)

    for link in links:
        status = "✅ Read" if link.is_read else "⏳ New"
        description = link.description or ""
        desc = description if full else description[:50] + "..." if len(description) > 50 else description
        tag = link.tag or ""
        date = link.created_at[:10] if link.created_at else ""

        table.add_row(str(link.id), status, link.url, desc, tag, date)

    console.print(table)


@app.command(rich_help_panel="Link Management")
@handle_errors
def search(
    query: str = typer.Argument(None, help="Search in URLs, descriptions, and tags"),
    domain: str = typer.Option("", "--domain", help="Filter by domain"),
    tag: str = typer.Option("", "--tag", "-t", help="Filter by tag"),
    read_only: bool = typer.Option(False, "--read-only", help="Show only read links"),
    unread_only: bool = typer.Option(False, "--unread-only", help="Show only unread links"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum results"),
) -> None:
    """Search your bookmarks with filters.

    All filters use AND logic (intersection).

    Examples:
        linkcovery search python                  # Search for 'python'
        linkcovery search --tag python            # Filter by tag only
        linkcovery search python --tag tools      # Search 'python' AND tag 'tools'
        linkcovery search --domain github.com     # Filter by domain only

    """
    link_service = _link_service()

    if not query and not domain and not tag:
        err_console.print("❌ No search query or filters provided", style="red")
        err_console.print("💡 Hint: linkcovery search <query> | --tag <tag> | --domain <domain>", style="yellow")
        raise typer.Exit(1)

    is_read = None
    if read_only:
        is_read = True
    elif unread_only:
        is_read = False

    results = link_service.search_links(
        query=query or "",
        domain=domain,
        tag=tag,
        is_read=is_read,
        limit=limit,
    )

    if state.json_mode:
        _emit_json([_link_dict(link) for link in results])
        return

    if not results:
        console.print("🔍 No matches found", style="yellow")
        return

    table = Table(title=f"🔍 Search Results ({len(results)} found)", box=None, header_style="dim")
    table.add_column("ID", style="cyan", width=4, justify="right")
    table.add_column("Status", width=6)
    table.add_column("URL", style="blue")
    table.add_column("Description", style="dim")
    table.add_column("Tag", style="magenta")

    for link in results:
        status = "✅" if link.is_read else "⏳"
        description = link.description or ""
        desc = description[:50] + "..." if len(description) > 50 else description
        tag = link.tag or ""

        table.add_row(str(link.id), status, link.url, desc, tag)

    console.print(table)


@app.command(rich_help_panel="Link Management")
@handle_errors
def show(link_id: int = typer.Argument(..., help="Link ID to display")) -> None:
    """Show detailed information about a specific link.

    Examples:
        linkcovery show 1

    """
    link_service = _link_service()
    link = link_service.get_link(link_id)

    if state.json_mode:
        _emit_json(_link_dict(link))
        return

    console.print(f"📖 Link #{link.id}", style="bold blue")
    console.print(f"   URL: {link.url}")
    console.print(f"   Domain: {link.domain}")
    console.print(f"   Description: {link.description or 'None'}")
    console.print(f"   Tag: {link.tag or 'None'}")
    console.print(f"   Status: {'✅ Read' if link.is_read else '⏳ Unread'}")
    console.print(f"   Created: {link.created_at}")
    console.print(f"   Updated: {link.updated_at}")


@app.command(rich_help_panel="Link Management")
@handle_errors
def edit(
    link_id: int = typer.Argument(..., help="Link ID to edit"),
    url: str | None = typer.Option(None, "--url", help="New URL"),
    description: str | None = typer.Option(None, "--desc", "-d", help="New description"),
    tag: str | None = typer.Option(None, "--tag", "-t", help="New tags"),
    read: bool = typer.Option(False, "--read", "-r", help="Mark as read"),
    unread: bool = typer.Option(False, "--unread", "-u", help="Mark as unread"),
) -> None:
    """Edit an existing link.

    Examples:
        linkcovery edit 1 --desc "New description"
        linkcovery edit 1 --url "https://newurl.com"

    """
    link_service = _link_service()

    is_read = None
    if read:
        is_read = True
    elif unread:
        is_read = False

    if not any([url, description is not None, tag is not None, is_read is not None]):
        err_console.print("⚠️ No updates specified", style="yellow")
        raise typer.Exit(1)

    link = link_service.update_link(
        link_id=link_id,
        url=url,
        description=description,
        tag=tag,
        is_read=is_read,
    )

    if state.json_mode:
        _emit_json(_link_dict(link))
        return

    console.print(f"✅ Updated link #{link.id}", style="green")


@app.command(rich_help_panel="Link Management")
@handle_errors
def delete(
    link_id: list[int] = typer.Argument(..., help="Link ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation (same as --force)"),
) -> None:
    """Delete a link from your bookmarks.

    Examples:
        linkcovery delete 1
        linkcovery delete 1 2 3
        linkcovery delete 1 --force

    """
    link_service = _link_service()

    links = [link_service.get_link(id) for id in link_id]

    if not force and not yes and not confirm_action(f"Delete links: {', '.join(str(link.id) for link in links)}?"):
        console.print("🛑 Deletion cancelled", style="yellow")
        return

    for link in links:
        link_service.delete_link(link.id)

    if state.json_mode:
        _emit_json({"deleted": [link.id for link in links]})
        return

    console.print(f"✅ Deleted links: {', '.join(str(link.id) for link in links)}", style="green")


@app.command(rich_help_panel="Link Management")
@handle_errors
def normalize(
    link_id: list[int] = typer.Argument(None, help="Link IDs to normalize"),
    all_links: bool = typer.Option(False, "--all", "-a", help="Normalize all links"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation for --all"),
) -> None:
    """Normalize link URLs by removing trailing slashes, converting http to https, and removing www.

    Examples:
        linkcovery normalize 1
        linkcovery normalize 1 2 3
        linkcovery normalize --all
        linkcovery normalize --all -y

    """
    link_service = _link_service()

    if all_links:
        if link_id:
            err_console.print("⚠️ Ignoring specific link IDs when --all is used", style="yellow")

        if not yes and not confirm_action("Normalize ALL links? This modifies URLs in bulk"):
            console.print("🛑 Normalization cancelled", style="yellow")
            return

        console.print("🔄 Normalizing all links...", style="blue")

        if normalized_links := link_service.normalize_all_links():
            if state.json_mode:
                _emit_json({"normalized": [_link_dict(link) for link in normalized_links]})
                return
            console.print(f"✅ Normalized {len(normalized_links)} links", style="green")
            for link in normalized_links:
                console.print(f"   • Link #{link.id}: {link.url}", style="dim")
        else:
            if state.json_mode:
                _emit_json({"normalized": []})
                return
            console.print("📭 No links found to normalize", style="yellow")
    elif link_id:
        failed = False
        normalized = []
        for id in link_id:
            try:
                link = link_service.normalize_link(id)
                normalized.append(_link_dict(link))
                console.print(f"✅ Normalized link #{link.id}: {link.url}", style="green")
            except Exception as e:
                failed = True
                err_console.print(f"❌ Failed to normalize link #{id}: {e}", style="red")

        if state.json_mode:
            _emit_json({"normalized": normalized, "failed": int(failed)})
        if failed:
            raise typer.Exit(1)
    else:
        err_console.print("❌ Please specify link IDs or use --all", style="red")
        err_console.print("💡 Hint: linkcovery normalize <id> | linkcovery normalize --all", style="yellow")
        raise typer.Exit(1)


@app.command(name="random", rich_help_panel="Link Management")
@handle_errors
def read_random(
    number: int = typer.Option(5, "--number", "-n", help="Number of random links to read"),
    include_read: bool = typer.Option(False, "--include-read", help="Include already read links"),
) -> None:
    """Read random links from your bookmarks and mark them as read.

    Examples:
        linkcovery random
        linkcovery random --number 10
        linkcovery random --include-read

    """
    link_service = _link_service()

    if number < 1:
        err_console.print("⚠️ Number must be at least 1", style="yellow")
        raise typer.Exit(1)

    links = link_service.get_random_links(number=number, unread_only=not include_read)

    if state.json_mode:
        _emit_json([_link_dict(link) for link in links])
        return

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


# Hidden legacy alias for 'random' (formerly 'read-random')
@app.command(name="read-random", hidden=True)
@handle_errors
def read_random_legacy(
    number: int = typer.Option(5, "--number", "-n", help="Number of random links to read"),
    include_read: bool = typer.Option(False, "--include-read", help="Include already read links"),
) -> None:
    """Alias for 'random' command."""
    read_random(number=number, include_read=include_read)
