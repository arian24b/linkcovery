"""Import and export service for LinkCovery."""

from asyncio import run as asyncio_run
from json import JSONDecodeError, dump, load
from pathlib import Path

from rich.progress import Progress, TaskID

from linkcovery.cli.cli_state import state
from linkcovery.core.chrome_bookmark import extractor
from linkcovery.core.exceptions import ImportExportError
from linkcovery.core.models import LinkExport
from linkcovery.core.utils import console, err_console, fetch_description
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
                if not state.json_mode:
                    console.print("📭 No links to export", style="yellow")
                return

            export_data = [LinkExport.from_db_link(link).model_dump() for link in links]

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                dump(export_data, f, indent=2, ensure_ascii=False)

            if not state.json_mode:
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
                if not state.json_mode:
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

        if not state.json_mode:
            err_console.print(f"📥 Importing {len(links_data)} links...")

        with Progress(console=err_console, disable=state.json_mode) as progress:
            task: TaskID = progress.add_task("Importing links...", total=len(links_data))

            for i, link_data in enumerate(links_data, 1):
                url = link_data.get("url")

                if not url or self.link_service.exists(url):
                    failed_count += 1
                    failed_links.append({"index": i, "url": url or "", "error": "URL missing or already exists"})
                    progress.update(task, advance=1)
                    continue

                try:
                    # show_spinner=False: a nested Status would corrupt the Progress bar
                    description = link_data.get("description", None)
                    if description is None:
                        description = asyncio_run(fetch_description(url=url, show_spinner=False))
                    self.link_service.add_link(
                        url=url,
                        description=description,
                        tag=link_data.get("tag", ""),
                        is_read=link_data.get("is_read", False),
                    )
                    added_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_links.append({"index": i, "url": link_data.get("url", ""), "error": str(e)})

                progress.update(task, advance=1)

        if not state.json_mode:
            console.print(f"✅ Import completed: {added_count} links added", style="green")
        if failed_count > 0:
            err_console.print(f"⚠️  {failed_count} links failed to import", style="yellow")
            for failure in failed_links:
                err_console.print(f"  #{failure['index']}: {failure['url']} - {failure['error']}")

    def import_from_txt(self, file_path: Path) -> None:
        """Import links from a text file (one URL per line)."""
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            msg = f"Failed to read file: {e}"
            raise ImportExportError(msg)

        urls = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]

        if not urls:
            if not state.json_mode:
                console.print("ℹ️ No links found in the text file", style="blue")
            return

        added_count = 0
        failed_count = 0
        failed_links = []

        if not state.json_mode:
            err_console.print(f"📥 Importing {len(urls)} links...")

        with Progress(console=err_console, disable=state.json_mode) as progress:
            task: TaskID = progress.add_task("Importing links...", total=len(urls))

            for i, url in enumerate(urls, 1):
                if self.link_service.exists(url):
                    failed_count += 1
                    failed_links.append({"index": i, "url": url or "", "error": "URL missing or already exists"})
                    progress.update(task, advance=1)
                    continue

                try:
                    self.link_service.add_link(url=url, description="", tag="", is_read=False)
                    added_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_links.append({"index": i, "url": url, "error": str(e)})

                progress.update(task, advance=1)

        if not state.json_mode:
            console.print(f"✅ Import completed: {added_count} links added", style="green")
        if failed_count > 0:
            err_console.print(f"⚠️  {failed_count} links failed to import", style="yellow")
            for failure in failed_links:
                err_console.print(f"  #{failure['index']}: {failure['url']} - {failure['error']}")

    def import_from_html(self, file_path: Path) -> None:
        """Import links from HTML file."""
        links = extractor(file_path)

        if not links:
            if not state.json_mode:
                console.print("ℹ️ No links found in the HTML file", style="blue")
            return

        added_count = 0
        failed_count = 0
        failed_links = []

        if not state.json_mode:
            err_console.print(f"📥 Importing {len(links)} links...")

        with Progress(console=err_console, disable=state.json_mode) as progress:
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
                        description=asyncio_run(fetch_description(url=link, show_spinner=False)),
                    )
                    added_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_links.append({"index": i, "url": link, "error": str(e)})

                progress.update(task, advance=1)

        if not state.json_mode:
            console.print(f"✅ Import completed: {added_count} links added", style="green")
        if failed_count > 0:
            err_console.print(f"⚠️  {failed_count} links failed to import", style="yellow")
            for failure in failed_links:
                err_console.print(f"  #{failure['index']}: {failure['url']} - {failure['error']}")

    def export_to_markdown(self, output_path: str | Path) -> str:
        """Export all links to Markdown format. Returns the content."""
        links = self.link_service.list_all_links()
        lines = ["# LinkCovery Bookmarks\n", f"_{len(links)} links exported_\n"]
        for link in links:
            tag = f" `[{link.tag}]`" if link.tag else ""
            status = " ✅ Read" if link.is_read else " ⏳ Unread"
            desc = f" — {link.description}" if link.description else ""
            lines.append(f"- [{link.url}]({link.url}){desc}{tag}{status}")
        content = "\n".join(lines)
        Path(output_path).write_text(content, encoding="utf-8")
        return content

    def export_to_html(self, output_path: str | Path) -> str:
        """Export all links to HTML format. Returns the content."""
        links = self.link_service.list_all_links()
        rows = []
        for link in links:
            tag = f'<span class="tag">{link.tag}</span>' if link.tag else ""
            status = "Read" if link.is_read else "Unread"
            desc = f"<p class=\"desc\">{link.description}</p>" if link.description else ""
            rows.append(f"""<tr>
            <td><a href="{link.url}" target="_blank" rel="noopener">{link.url}</a>{desc}</td>
            <td>{tag}</td>
            <td><span class="status-{'read' if link.is_read else 'unread'}">{status}</span></td>
            </tr>""")
        content = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LinkCovery Bookmarks</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 0 auto; padding: 20px; background: #f7f7f4; color: #1d1f1f; }}
h1 {{ font-size: 24px; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.06); }}
th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e3e6e8; }}
th {{ background: #eef0f1; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: #6b6f72; }}
.desc {{ font-size: 13px; color: #6b6f72; margin: 4px 0 0; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; background: #e1f0eb; color: #1f7a5a; }}
.status-read {{ color: #1f7a5a; font-weight: 600; }}
.status-unread {{ color: #d55c3a; font-weight: 600; }}
a {{ color: #1f7a5a; text-decoration: none; font-weight: 500; }}
</style>
</head>
<body>
<h1>LinkCovery Bookmarks</h1>
<p style="color:#6b6f72">{len(links)} links exported</p>
<table><thead><tr><th>URL</th><th>Tag</th><th>Status</th></tr></thead><tbody>
{"".join(rows)}
</tbody></table>
</body>
</html>"""
        Path(output_path).write_text(content, encoding="utf-8")
        return content

    def export_links(self, links: list, output_path: str | Path) -> None:
        """Export a specific list of links."""
        try:
            output_path = Path(output_path)
            export_data = [LinkExport.from_db_link(link).model_dump() for link in links]

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                dump(export_data, f, indent=2, ensure_ascii=False)

            if not state.json_mode:
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
