"""Core utilities for LinKCovery."""

import functools
from collections.abc import Callable
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlparse

from httpx import AsyncClient
from rich.console import Console
from typer import Exit

from linkcovery.core.exceptions import LinKCoveryError

console = Console()


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors gracefully in CLI commands."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except LinKCoveryError as e:
            console.print(f"❌ {e.message}", style="red")
            if e.details:
                console.print(f"   {e.details}", style="dim red")
            if e.hint:
                console.print(f"💡 Hint: {e.hint}", style="yellow")
            raise Exit(1)
        except KeyboardInterrupt:
            console.print("\n🛑 Operation cancelled by user", style="yellow")
            raise Exit(130)
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}", style="red")
            if console._environ.get("LINKCOVERY_DEBUG"):  # type: ignore
                import traceback

                traceback.print_exc()
            raise Exit(1)

    return wrapper


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask for user confirmation."""
    try:
        from rich.prompt import Confirm

        return Confirm.ask(message, default=default)
    except KeyboardInterrupt:
        console.print("\n🛑 Operation cancelled", style="yellow")
        return False


def extract_domain(url: str) -> str:
    """Extract domain from the URL."""
    try:
        return urlparse(url).netloc.lower().strip().removeprefix("www.")
    except Exception:
        msg = "Could not extract domain from URL"
        raise ValueError(msg)


def normalize_url(url: str) -> str:
    """Normalize URL by removing trailing slash, converting http to https, and removing www from domain."""
    try:
        parsed = urlparse(url)

        # Remove www from domain
        netloc = parsed.netloc.lower().removeprefix("www.")

        # Remove trailing slash from path
        path = parsed.path.rstrip("/") if parsed.path != "/" else ""

        # Reconstruct the URL
        normalized = f"https://{netloc}{path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        if parsed.fragment:
            normalized += f"#{parsed.fragment}"

        return normalized
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
            if attrs.get("name", "").lower() == "description":
                self.description = attrs.get("content", "").strip()


async def fetch_description(url: str, timeout: int = 10, show_spinner: bool = True) -> str:
    """Fetch page description from URL.

    Args:
        url: URL to fetch description from
        timeout: Timeout in seconds (default: 10)
        show_spinner: Whether to show loading spinner (default: True)

    Returns:
        Fetched description or empty string on failure

    """
    if show_spinner:
        from rich.status import Status

        with Status("📥 Fetching metadata...", console=console):
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
