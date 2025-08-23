"""Import and export service for LinKCovery."""

from asyncio import run as asyncio_run
from json import JSONDecodeError, dump
from json import load as j_load
from pathlib import Path

from rich.progress import Progress, TaskID

from linkcovery.core.exceptions import ImportExportError
from linkcovery.core.models import LinkExport
from linkcovery.core.utils import console, fetch_description_and_tags
from linkcovery.services import get_link_service
from linkcovery.services.link_service import LinkService


class DataService:
    """Service for handling data operations."""

    def __init__(self, link_service: LinkService | None = None) -> None:
        """Initialize with link service dependency."""
        self.link_service = link_service or get_link_service()

    def export_to_json(self, output_path: str | Path) -> None:
        """Export all links to JSON format."""
        try:
            output_path = Path(output_path)
            links = self.link_service.list_all_links()

            if not links:
                console.print("📭 No links to export", style="yellow")
                return

            # Convert to export format
            export_data = [LinkExport.from_db_link(link).model_dump() for link in links]

            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                dump(export_data, f, indent=2, ensure_ascii=False)

            console.print(f"✅ Successfully exported {len(links)} links to {output_path}", style="green")

        except Exception as e:
            msg = f"Failed to export links: {e}"
            raise ImportExportError(msg)

    def import_from_json(self, input_path: str | Path) -> None:
        """Import links from JSON file."""
        input_path = Path(input_path)

        if not input_path.exists():
            msg = f"File not found: {input_path}"
            raise ImportExportError(msg)

        try:
            with open(input_path, encoding="utf-8") as f:
                links_data = j_load(f)
        except JSONDecodeError as e:
            msg = f"Invalid JSON format: {e}"
            raise ImportExportError(msg)
        except Exception as e:
            msg = f"Failed to read file: {e}"
            raise ImportExportError(msg)

        if not links_data:
            console.print("ℹ️ No links found in the JSON file", style="blue")
            return

        # Import with progress tracking
        added_count = 0
        failed_count = 0
        failed_links = []

        console.print(f"📥 Importing {len(links_data)} links...")

        with Progress() as progress:
            task: TaskID = progress.add_task("Importing links...", total=len(links_data))

            for i, link_data in enumerate(links_data, 1):
                try:
                    url = link_data.get("url", "")
                    description = link_data.get("description", "")
                    tag = link_data.get("tag", "")
                    is_read = link_data.get("is_read", False)

                    self.link_service.add_link(
                        url=url,
                        description=description,
                        tag=tag,
                        is_read=is_read,
                    )
                    added_count += 1

                except Exception as e:
                    failed_count += 1
                    failed_links.append({"index": i, "url": url, "error": str(e)})

                progress.update(task, advance=1)

        # Show results
        console.print(f"✅ Import completed: {added_count} links added", style="green")
        if failed_count > 0:
            console.print(f"⚠️  {failed_count} links failed to import", style="yellow")
            if failed_links[:5]:  # Show first 5 failures
                console.print("First few failures:")
                for failure in failed_links[:5]:
                    console.print(f"  #{failure['index']}: {failure['url']} - {failure['error']}")

    def import_from_html(self, input_path: str | Path) -> None:
        """Import links from HTML file."""
        from bs4 import BeautifulSoup

        try:
            with open(input_path, encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                links_data = []
                for a in soup.find_all("a"):
                    url = a.get("href", "")
                    links_data.append({"url": url, "description": ""})

        except Exception as e:
            msg = f"Failed to read file: {e}"
            raise ImportExportError(msg)

        if not links_data:
            console.print("ℹ️ No links found in the HTML file", style="blue")
            return

        # Import with progress tracking
        added_count = 0
        failed_count = 0
        failed_links = []

        console.print(f"📥 Importing {len(links_data)} links...")

        with Progress() as progress:
            task: TaskID = progress.add_task("Importing links...", total=len(links_data))

            for i, link_data in enumerate(links_data, 1):
                try:
                    url = link_data.get("url", "")
                    description = link_data.get("description")
                    tag = link_data.get("tag")
                    is_read = link_data.get("is_read", False)

                    if not (tag and description):
                        fetch = asyncio_run(fetch_description_and_tags(url=url))
                        final_description = description or fetch["description"]
                        final_tag = tag or fetch["tags"]

                    self.link_service.add_link(
                        url=url,
                        description=final_description,
                        tag=final_tag,
                        is_read=is_read,
                    )
                    added_count += 1

                except Exception as e:
                    failed_count += 1
                    failed_links.append({"index": i, "url": url, "error": str(e)})

                progress.update(task, advance=1)

        # Show results
        console.print(f"✅ Import completed: {added_count} links added", style="green")

    def export_links(self, links: list, output_path: str | Path) -> None:
        """Export a specific list of links."""
        try:
            output_path = Path(output_path)
            export_data = [LinkExport.from_db_link(link).model_dump() for link in links]

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                dump(export_data, f, indent=2, ensure_ascii=False)

            console.print(f"✅ Successfully exported {len(links)} links to {output_path}", style="green")

        except Exception as e:
            msg = f"Failed to export links: {e}"
            raise ImportExportError(msg)
