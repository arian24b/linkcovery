"""Core utilities for LinKCovery."""

import functools
from collections.abc import Callable
from html.parser import HTMLParser
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin, urlparse, urlunparse

from rich.console import Console
from typer import Exit

from linkcovery.core.exceptions import LinKCoveryError

if TYPE_CHECKING:
    pass

# Stdout console for command output (tables, results).
console = Console()
# Stderr console for diagnostics: errors, warnings, progress, spinners.
err_console = Console(stderr=True)


def _error_payload(e: Exception) -> dict[str, Any]:
    """Build the machine-readable error payload for --json mode."""
    payload: dict[str, Any] = {"error": str(getattr(e, "message", e)) or e.__class__.__name__}
    for key in ("details", "hint"):
        if getattr(e, key, ""):
            payload[key] = getattr(e, key)
    return payload


def _print_error(e: Exception, *, unexpected: bool = False) -> None:
    """Print an error to stderr, as text or JSON depending on CLI state."""
    import json

    from linkcovery.cli.cli_state import state

    if state.json_mode:
        err_console.print(json.dumps(_error_payload(e)), soft_wrap=True, markup=False, highlight=False)
        return

    if unexpected:
        err_console.print(f"❌ Unexpected error: {e}", style="red")
        return

    assert isinstance(e, LinKCoveryError)  # narrowed: callers guarantee this
    err_console.print(f"❌ {e.message}", style="red")
    if e.details:
        err_console.print(f"   {e.details}", style="dim red")
    if e.hint:
        err_console.print(f"💡 Hint: {e.hint}", style="yellow")


def _print_cancelled() -> None:
    """Report Ctrl-C on stderr, honoring --json mode."""
    import json

    from linkcovery.cli.cli_state import state

    if state.json_mode:
        payload = {"error": "cancelled", "hint": "Interrupted by user"}
        err_console.print(json.dumps(payload), soft_wrap=True, markup=False, highlight=False)
    else:
        err_console.print("\n🛑 Operation cancelled by user", style="yellow")


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors gracefully in CLI commands.

    Exit codes: LinKCoveryError/unexpected error -> 1, Ctrl-C -> 130.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exit:
            raise
        except LinKCoveryError as e:
            _print_error(e)
            raise Exit(1)
        except KeyboardInterrupt:
            _print_cancelled()
            raise Exit(130)
        except Exception as e:
            _print_error(e, unexpected=True)
            if err_console._environ.get("LINKCOVERY_DEBUG"):  # type: ignore[attr-defined]
                import traceback

                traceback.print_exc()
            raise Exit(1)

    return wrapper


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask for user confirmation.

    Raises:
        KeyboardInterrupt: Propagated so handle_errors turns it into exit code 130.
    """
    from rich.prompt import Confirm

    return Confirm.ask(message, default=default)


def extract_domain(url: str) -> str:
    """Extract domain from the URL."""
    try:
        return urlparse(url).netloc.lower().strip().removeprefix("www.")
    except Exception:
        msg = "Could not extract domain from URL"
        raise ValueError(msg)


def normalize_url(url: str) -> str:
    """Normalize URL by removing trailing slash and removing www from domain."""
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme or "https"
        hostname = (parsed.hostname or "").lower().removeprefix("www.")

        netloc = hostname
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        if parsed.username:
            userinfo = parsed.username
            if parsed.password:
                userinfo = f"{userinfo}:{parsed.password}"
            netloc = f"{userinfo}@{netloc}"

        path = parsed.path.rstrip("/") if parsed.path != "/" else ""

        return urlunparse((scheme, netloc, path, parsed.params, parsed.query, parsed.fragment))
    except Exception:
        msg = "Could not normalize URL"
        raise ValueError(msg)


class DescriptionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.description = ""

    def handle_starttag(self, tag, attrs) -> None:
        if tag.lower() == "meta":
            attrs = dict(attrs)

            # match: <meta name="description" content="...">
            if (attrs.get("name") or "").lower() == "description":
                self.description = (attrs.get("content") or "").strip()


class PreviewParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.og_image = ""
        self.first_img = ""

    def handle_starttag(self, tag, attrs) -> None:
        attrs = dict(attrs)
        if tag.lower() == "meta" and (attrs.get("property") or "").lower() == "og:image":
            self.og_image = (attrs.get("content") or "").strip()
        if tag.lower() == "img" and not self.first_img:
            self.first_img = (attrs.get("src") or "").strip()


async def _fetch_description_inner(url: str, timeout: int) -> str:
    """Fetch and parse the meta description for a URL (no spinner)."""
    from httpx import AsyncClient

    try:
        async with AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            verify=False,
            http2=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except Exception:
        return ""
    parser = DescriptionParser()
    parser.feed(resp.text)
    return parser.description


async def fetch_description(url: str, timeout: int = 10, show_spinner: bool = True) -> str:
    """Fetch page description from URL.

    Args:
        url: URL to fetch description from
        timeout: Timeout in seconds (default: 10)
        show_spinner: Whether to show loading spinner (default: True)

    Returns:
        Fetched description or empty string on failure
    """
    from linkcovery.cli.cli_state import state

    if state.json_mode:
        show_spinner = False

    if show_spinner:
        from rich.status import Status

        with Status("📥 Fetching metadata...", console=err_console):
            return await _fetch_description_inner(url, timeout)
    return await _fetch_description_inner(url, timeout)


async def fetch_preview_image(url: str, timeout: int = 10) -> str:
    """Fetch og:image or first image URL from a page."""
    from httpx import AsyncClient

    try:
        async with AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            verify=False,
            http2=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except Exception:
        return ""

    parser = PreviewParser()
    parser.feed(resp.text)
    if parser.og_image:
        return urljoin(str(resp.url), parser.og_image)
    if parser.first_img:
        return urljoin(str(resp.url), parser.first_img)
    return ""
