"""Core utilities for LinKCovery."""

import functools
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

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


async def fetch_description_and_tags(url: str) -> dict[str, str]:
    """Fetch metadata from URL. Imports are lazy-loaded for performance."""
    try:
        # Lazy imports to avoid loading HTTP libraries unless needed
        import httpx
        from bs4 import BeautifulSoup

        async with httpx.AsyncClient(
            timeout=10,  # Reduced timeout for better performance
            follow_redirects=True,
            verify=False,
            http2=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag.get("content", "").strip() if description_tag else ""

        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag and "content" in keywords_tag.attrs:
            # Format like: tag1,tag2,tag3,
            tags = ",".join(kw.strip() for kw in keywords_tag["content"].split(",")) + ","
        else:
            tags = ""

        return {"description": description, "tags": tags}
    except Exception:
        # Return empty values if fetching fails
        return {"description": "", "tags": ""}
