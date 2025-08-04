"""Simple utilities for LinKCovery."""

import json
from pathlib import Path
from urllib.parse import urlparse

from rich import print


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


def export_links_to_json(output_path: str) -> None:
    """Export all links to JSON format."""
    try:
        from linkcovery.core.database import get_database

        db = get_database()
        links = db.get_all_links()

        links_data = []
        for link in links:
            links_data.append(
                {
                    "id": link.id,
                    "url": link.url,
                    "domain": link.domain,
                    "description": link.description,
                    "tag": link.tag,
                    "is_read": link.is_read,
                    "created_at": link.created_at,
                    "updated_at": link.updated_at,
                },
            )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(links_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Successfully exported {len(links_data)} links to {output_path}")

    except Exception as e:
        print(f"❌ Failed to export links: {e}")


def import_links_from_json(file_path: str) -> None:
    """Import links from JSON file."""
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return

    try:
        with open(file_path, encoding="utf-8") as f:
            links_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return

    if not links_data:
        print("ℹ️  No links found in the JSON file")
        return

    from linkcovery.core.database import get_database

    db = get_database()
    added_count = 0
    failed_count = 0

    for i, link_data in enumerate(links_data, 1):
        try:
            url = link_data.get("url", "")
            if not validate_url(url):
                print(f"⚠️  Skipping invalid URL at index {i}: {url}")
                failed_count += 1
                continue

            # Extract fields with defaults
            description = link_data.get("description", "")
            tag = link_data.get("tag", "")
            is_read = link_data.get("is_read", False)

            db.add_link(url=url, description=description, tag=tag, is_read=is_read)
            added_count += 1

        except ValueError as e:
            if "already exists" in str(e):
                print(f"⚠️  Link already exists at index {i}: {url}")
            else:
                print(f"⚠️  Failed to import link at index {i}: {e}")
            failed_count += 1
        except Exception as e:
            print(f"⚠️  Failed to import link at index {i}: {e}")
            failed_count += 1

    print(f"✅ Import completed: {added_count} links added, {failed_count} failed")
