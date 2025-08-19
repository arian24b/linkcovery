"""Core utilities for LinKCovery."""

from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Simple URL validation."""
    try:
        if not url or not isinstance(url, str):
            return False
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            return False
        result = urlparse(url)
        return bool(result.scheme and result.netloc)
    except Exception:
        return False


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


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
