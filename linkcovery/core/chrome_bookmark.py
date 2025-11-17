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
