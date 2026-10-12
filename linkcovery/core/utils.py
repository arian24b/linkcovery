"""Core utilities for LinKCovery."""

import functools
import os
from collections.abc import Callable
from html.parser import HTMLParser
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin, urlparse, urlunparse

from cfui import Fail, ui

from linkcovery.core.exceptions import LinKCoveryError

if TYPE_CHECKING:
    pass


def print_json(payload) -> None:
    """Stdout JSON, no markup, so pipes stay parseable."""
    import json

    print(json.dumps(payload, ensure_ascii=False, default=str))


def _error_payload(e: Exception) -> dict[str, Any]:
    """Build the machine-readable error payload for --json mode."""
    payload: dict[str, Any] = {"error": str(getattr(e, "message", e)) or e.__class__.__name__}
    for key in ("details", "hint"):
        if getattr(e, key, ""):
            payload[key] = getattr(e, key)
    return payload


def handle_errors(func: Callable) -> Callable:
    """Turn LinKCoveryError / unexpected errors into cfui boxed errors (or a JSON error with --json). Exit 1."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        from linkcovery.cli.cli_state import state

        try:
            return func(*args, **kwargs)
        except (Fail, SystemExit, KeyboardInterrupt):
            raise
        except Exception as e:
            known = isinstance(e, LinKCoveryError)
            if state.json_mode:
                import json
                import sys

                print(json.dumps(_error_payload(e)), file=sys.stderr)
                raise SystemExit(1) from None
            if not known and os.environ.get("LINKCOVERY_DEBUG"):
                import traceback

                traceback.print_exc()
            hint = " ".join(x for x in (getattr(e, "details", ""), getattr(e, "hint", "")) if x) or None
            raise Fail(e.message if known else f"Unexpected error: {e}", hint) from None

    return wrapper


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask for confirmation; non-interactive runs must pass --yes."""
    if not ui.interactive():
        raise Fail(f"{message}", "Not a terminal: pass --yes to confirm.", code=2)
    return ui.confirm(message, default=default)


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
        ui.info("Fetching metadata...")
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
