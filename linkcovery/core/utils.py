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
