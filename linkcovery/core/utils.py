"""Core utilities for LinKCovery."""

import functools
from collections.abc import Callable
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

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


async def fetch_preview_image(url: str, timeout: int = 10) -> str:
    """Fetch og:image or first image URL from a page."""
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
