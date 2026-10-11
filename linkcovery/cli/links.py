"""Link management commands for LinkCovery CLI."""

import asyncio
from asyncio import run as asyncio_run
from collections.abc import Callable

from cfui import Arg, ui

from linkcovery.cli.app import app as cli
from linkcovery.cli.app import command
from linkcovery.cli.cli_state import state
from linkcovery.core.utils import confirm_action, fetch_description, handle_errors


def _link_service():
    from linkcovery.services.link_service import get_link_service

    return get_link_service()


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
    from linkcovery.core.utils import print_json

    print_json(payload)


@command(
    cli,
    "add",
    "Add a new link to your bookmarks",
    aliases=("new",),
    args=[
        Arg("url", required=True, prompt="URL to bookmark", help="URL to bookmark"),
        Arg("-d", "--desc", dest="description", default="", help="Description for link"),
        Arg("-t", "--tag", help="Tag to categorize link"),
        Arg("-r", "--read", action="store_true", help="Mark as already read"),
        Arg("--no-fetch", action="store_true", help="Skip fetching metadata from URL"),
        Arg("--timeout", type=int, default=10, help="Timeout for fetching metadata (seconds)"),
    ],
)
@handle_errors
def add(url, description, tag, read, no_fetch, timeout) -> None:
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

    ui.success(f"Added link #{link.id}")
    ui.out(f"   URL: {url}")


@command(
    cli,
    "list",
    "List your bookmarked links",
    aliases=("ls",),
    args=[
        Arg("-l", "--limit", type=int, default=20, help="Maximum number of links to show"),
        Arg("--read-only", action="store_true", help="Show only read links"),
        Arg("--unread-only", action="store_true", help="Show only unread links"),
        Arg("--full", action="store_true", help="Show full descriptions without truncation"),
    ],
)
@handle_errors
def list_links(limit, read_only, unread_only, full) -> None:
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
        ui.warning("No links found")
        return

    rows = []
    for link in links:
        description = link.description or ""
        desc = description if full else description[:50] + "..." if len(description) > 50 else description
        rows.append(
            (link.id, "read" if link.is_read else "new", link.url, desc, link.tag or "", (link.created_at or "")[:10])
        )
    ui.table(rows, ["ID", "Status", "URL", "Description", "Tag", "Added"])


@command(
    cli,
    "search",
    "Search your bookmarks with filters (all filters are ANDed)",
    aliases=("find",),
    args=[
        Arg("query", nargs="?", help="Search in URLs, descriptions, and tags"),
        Arg("--domain", default="", help="Filter by domain"),
        Arg("-t", "--tag", default="", help="Filter by tag"),
        Arg("--read-only", action="store_true", help="Show only read links"),
        Arg("--unread-only", action="store_true", help="Show only unread links"),
        Arg("-l", "--limit", type=int, default=20, help="Maximum results"),
    ],
)
@handle_errors
def search(query, domain, tag, read_only, unread_only, limit) -> None:
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
        ui.error("No search query or filters provided")
        ui.hint("linkcovery search <query> | --tag <tag> | --domain <domain>")
        raise SystemExit(1)

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
        ui.warning("No matches found")
        return

    ui.table(
        [
            (
                link.id,
                "read" if link.is_read else "new",
                link.url,
                (link.description or "")[:50] + ("..." if len(link.description or "") > 50 else ""),
                link.tag or "",
            )
            for link in results
        ],
        ["ID", "Status", "URL", "Description", "Tag"],
    )


@command(
    cli,
    "show",
    "Show detailed information about a specific link",
    args=[Arg("link_id", type=int, required=True, prompt="Link ID", help="Link ID to display")],
)
@handle_errors
def show(link_id) -> None:
    """Show detailed information about a specific link.

    Examples:
        linkcovery show 1

    """
    link_service = _link_service()
    link = link_service.get_link(link_id)

    if state.json_mode:
        _emit_json(_link_dict(link))
        return

    ui.heading(f"Link #{link.id}")
    ui.out(f"   URL: {link.url}")
    ui.out(f"   Domain: {link.domain}")
    ui.out(f"   Description: {link.description or 'None'}")
    ui.out(f"   Tag: {link.tag or 'None'}")
    ui.out(f"   Status: {'✅ Read' if link.is_read else '⏳ Unread'}")
    ui.out(f"   Created: {link.created_at}")
    ui.out(f"   Updated: {link.updated_at}")


@command(
    cli,
    "edit",
    "Edit an existing link",
    args=[
        Arg("link_id", type=int, required=True, prompt="Link ID", help="Link ID to edit"),
        Arg("--url", help="New URL"),
        Arg("-d", "--desc", dest="description", help="New description"),
        Arg("-t", "--tag", help="New tags"),
        Arg("-r", "--read", action="store_true", help="Mark as read"),
        Arg("-u", "--unread", action="store_true", help="Mark as unread"),
    ],
)
@handle_errors
def edit(link_id, url, description, tag, read, unread) -> None:
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
        ui.warning("No updates specified")
        raise SystemExit(1)

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

    ui.success(f"Updated link #{link.id}")


@command(
    cli,
    "delete",
    "Delete links from your bookmarks",
    aliases=("rm",),
    args=[
        Arg("link_id", type=int, nargs="+", required=True, prompt="Link IDs to delete", help="Link IDs to delete"),
        Arg("-f", "--force", action="store_true", help="Skip confirmation"),
        Arg("-y", "--yes", action="store_true", help="Skip confirmation (same as --force)"),
    ],
)
@handle_errors
def delete(link_id, force, yes) -> None:
    """Delete a link from your bookmarks.

    Examples:
        linkcovery delete 1
        linkcovery delete 1 2 3
        linkcovery delete 1 --force

    """
    link_service = _link_service()

    links = [link_service.get_link(id) for id in link_id]

    if not force and not yes and not confirm_action(f"Delete links: {', '.join(str(link.id) for link in links)}?"):
        ui.warning("Deletion cancelled")
        return

    for link in links:
        link_service.delete_link(link.id)

    if state.json_mode:
        _emit_json({"deleted": [link.id for link in links]})
        return

    ui.success(f"Deleted links: {', '.join(str(link.id) for link in links)}")


@command(
    cli,
    "normalize",
    "Normalize link URLs (trailing slash, http to https, www)",
    args=[
        Arg("link_id", type=int, nargs="*", help="Link IDs to normalize"),
        Arg("-a", "--all", dest="all_links", action="store_true", help="Normalize all links"),
        Arg("-y", "--yes", action="store_true", help="Skip confirmation for --all"),
    ],
)
@handle_errors
def normalize(link_id, all_links, yes) -> None:
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
            ui.warning("Ignoring specific link IDs when --all is used")

        if not yes and not confirm_action("Normalize ALL links? This modifies URLs in bulk"):
            ui.warning("Normalization cancelled")
            return

        ui.info("Normalizing all links...")

        if normalized_links := link_service.normalize_all_links():
            if state.json_mode:
                _emit_json({"normalized": [_link_dict(link) for link in normalized_links]})
                return
            ui.success(f"Normalized {len(normalized_links)} links")
            for link in normalized_links:
                ui.hint(f"   • Link #{link.id}: {link.url}")
        else:
            if state.json_mode:
                _emit_json({"normalized": []})
                return
            ui.warning("No links found to normalize")
    elif link_id:
        failed = False
        normalized = []
        for id in link_id:
            try:
                link = link_service.normalize_link(id)
                normalized.append(_link_dict(link))
                ui.success(f"Normalized link #{link.id}: {link.url}")
            except Exception as e:
                failed = True
                ui.error(f"Failed to normalize link #{id}: {e}")

        if state.json_mode:
            _emit_json({"normalized": normalized, "failed": int(failed)})
        if failed:
            raise SystemExit(1)
    else:
        ui.error("Please specify link IDs or use --all")
        ui.hint("linkcovery normalize <id> | linkcovery normalize --all")
        raise SystemExit(1)


@command(
    cli,
    "describe",
    "Fetch and fill in missing descriptions for links",
    args=[
        Arg("link_id", type=int, nargs="*", help="Link IDs to describe"),
        Arg("-a", "--all", dest="all_links", action="store_true", help="Update descriptions for ALL links"),
        Arg("-y", "--yes", action="store_true", help="Skip confirmation for --all"),
        Arg("-c", "--concurrency", type=int, default=30, help="Maximum parallel fetches"),
        Arg("--timeout", type=int, default=10, help="Fetch timeout in seconds"),
    ],
)
@handle_errors
def describe(link_id, all_links, yes, concurrency, timeout) -> None:
    """Fetch and fill in missing descriptions for links.

    Without arguments, only links with an empty description are fetched
    (links whose fetch returns nothing are counted as skipped, not failed).

    Examples:
        linkcovery describe
        linkcovery describe 1 2 3
        linkcovery describe --all
        linkcovery describe --all -y

    """
    link_service = _link_service()

    if all_links:
        if link_id:
            ui.warning("Ignoring specific link IDs when --all is used")

        if not yes and not confirm_action("Fetch descriptions for ALL links? This overwrites existing descriptions"):
            ui.warning("Description update cancelled")
            return

        links = link_service.list_all_links()
    elif link_id:
        links = []
        for raw_id in link_id:
            try:
                links.append(link_service.get_link(raw_id))
            except Exception as e:
                ui.error(f"Failed to describe link #{raw_id}: {e}")
        if len(links) < len(link_id):
            raise SystemExit(1)
    else:
        links = [link for link in link_service.list_all_links() if not link.description.strip()]

    if not links:
        if state.json_mode:
            _emit_json({"updated": [], "skipped": 0, "failed": 0})
            return
        ui.warning("No links found needing descriptions")
        return

    async def _fetch_all(on_done: Callable[[], None]) -> list[tuple[int, str]]:
        sem = asyncio.Semaphore(concurrency)

        async def one(_id: int, url: str) -> tuple[int, str]:
            async with sem:
                result = _id, await fetch_description(url=url, timeout=timeout, show_spinner=False)
            on_done()
            return result

        return await asyncio.gather(*(one(link.id, str(link.url)) for link in links))

    with ui.progress("Fetching descriptions", len(links), enabled=not state.json_mode) as progress:
        results = asyncio_run(_fetch_all(progress.advance))

    updated: list[dict] = []
    skipped = 0
    failed = 0

    for link_id_, desc in results:
        if not desc.strip():
            skipped += 1
            continue
        try:
            link = link_service.update_link(link_id=link_id_, description=desc)
            updated.append(_link_dict(link))
            if not state.json_mode:
                ui.success(f"Described link #{link.id}: {desc[:50]}")
        except Exception as e:
            failed += 1
            ui.error(f"Failed to update link #{link_id_}: {e}")

    if state.json_mode:
        _emit_json({"updated": updated, "skipped": skipped, "failed": failed})
    else:
        ui.info(f"Descriptions: {len(updated)} updated, {skipped} skipped, {failed} failed")

    if failed:
        raise SystemExit(1)


@command(
    cli,
    "random",
    "Read random links and mark them as read",
    args=[
        Arg("-n", "--number", type=int, default=5, help="Number of random links to read"),
        Arg("--include-read", action="store_true", help="Include already read links"),
    ],
)
@handle_errors
def read_random(number, include_read) -> None:
    """Read random links from your bookmarks and mark them as read.

    Examples:
        linkcovery random
        linkcovery random --number 10
        linkcovery random --include-read

    """
    link_service = _link_service()

    if number < 1:
        ui.warning("Number must be at least 1")
        raise SystemExit(1)

    links = link_service.get_random_links(number=number, unread_only=not include_read)

    if state.json_mode:
        _emit_json([_link_dict(link) for link in links])
        return

    if not links:
        filter_msg = "unread " if not include_read else ""
        ui.warning(f"No {filter_msg}links available to read")
        return

    ui.heading(f"Reading {len(links)} random link{'s' if len(links) > 1 else ''}:")

    for link in links:
        ui.info(f"Reading link #{link.id}: {link.url}")
        if link.description:
            ui.hint(f"{link.description}")

        # Only mark as read if it wasn't already read
        if not link.is_read:
            link_service.mark_as_read(link.id)
            ui.success("Marked as read")
        else:
            ui.hint("Already read")
        ui.out()
