"""Import and export service for LinKCovery."""

from asyncio import run as asyncio_run
from json import JSONDecodeError, dump, load
from pathlib import Path

from rich.progress import Progress, TaskID

from linkcovery.core.chrome_bookmark import extractor
from linkcovery.core.exceptions import ImportExportError
from linkcovery.core.models import LinkExport
from linkcovery.core.utils import console, fetch_description
from linkcovery.services.link_service import LinkService, get_link_service


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

    def import_from_json(self, file_path: Path) -> None:
        """Import links from JSON file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                links_data = load(f)
            if not links_data:
                console.print("ℹ️ No links found in the JSON file", style="blue")
                return
        except JSONDecodeError as e:
            msg = f"Invalid JSON format: {e}"
            raise ImportExportError(msg)
        except Exception as e:
            msg = f"Failed to read file: {e}"
            raise ImportExportError(msg)

        added_count = 0
        failed_count = 0
        failed_links = []

        console.print(f"📥 Importing {len(links_data)} links...")

        with Progress() as progress:
            task: TaskID = progress.add_task("Importing links...", total=len(links_data))

            for i, link_data in enumerate(links_data, 1):
                url = link_data.get("url")

                if not url or self.link_service.exists(url):
                    failed_count += 1
                    failed_links.append({"index": i, "url": url or "", "error": "URL missing or already exists"})
                    progress.update(task, advance=1)
                    continue

                try:
                    self.link_service.add_link(
                        url=url,
                        description=link_data.get("description", asyncio_run(fetch_description(url=url))),
                        tag=link_data.get("tag", ""),
                        is_read=link_data.get("is_read", False),
                    )
                    added_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_links.append({"index": i, "url": link_data.get("url", ""), "error": str(e)})

                progress.update(task, advance=1)

        console.print(f"✅ Import completed: {added_count} links added", style="green")
        if failed_count > 0:
            console.print(f"⚠️  {failed_count} links failed to import", style="yellow")
            for failure in failed_links:
                console.print(f"  #{failure['index']}: {failure['url']} - {failure['error']}")

    def import_from_html(self, file_path: Path) -> None:
        """Import links from HTML file."""
        links = extractor(file_path)

        if not links:
            console.print("ℹ️ No links found in the HTML file", style="blue")
            return

        added_count = 0
        failed_count = 0
        failed_links = []

        console.print(f"📥 Importing {len(links)} links...")

        with Progress() as progress:
            task: TaskID = progress.add_task("Importing links...", total=len(links))

            for i, link in enumerate(links, 1):
                if not link or self.link_service.exists(link):
                    failed_count += 1
                    failed_links.append({"index": i, "url": link or "", "error": "URL missing or already exists"})
                    progress.update(task, advance=1)
                    continue

                try:
                    self.link_service.add_link(
                        url=link,
                        description=asyncio_run(fetch_description(url=link)),
                    )
                    added_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_links.append({"index": i, "url": link, "error": str(e)})

                progress.update(task, advance=1)

        console.print(f"✅ Import completed: {added_count} links added", style="green")
        if failed_count > 0:
            console.print(f"⚠️  {failed_count} links failed to import", style="yellow")
            for failure in failed_links:
                console.print(f"  #{failure['index']}: {failure['url']} - {failure['error']}")

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


# Global service instance
_data_service: DataService | None = None


def get_data_service() -> DataService:
    """Get the global import/export service instance."""
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service
