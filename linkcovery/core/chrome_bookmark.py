from html.parser import HTMLParser
from pathlib import Path


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag == "a":
            attrs = dict(attrs)
            href = attrs.get("href")
            if href:
                self.links.append(href)


def extractor(file_path: Path) -> list[str]:
    content = file_path.read_text(encoding="utf-8")
    parser = LinkParser()
    parser.feed(content)
    return parser.links


def default_chrome_bookmarks() -> Path:
    """Usual Chrome bookmarks location for this OS."""
    import platform

    system = platform.system()
    home = Path.home()
    if system == "Darwin":
        return home / "Library/Application Support/Google/Chrome/Default/Bookmarks"
    if system == "Windows":
        from os import getenv

        return Path(getenv("LOCALAPPDATA", str(home))) / "Google/Chrome/User Data/Default/Bookmarks"
    return home / ".config/google-chrome/Default/Bookmarks"
