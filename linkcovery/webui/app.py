"""FastAPI Web UI for LinkCovery."""

from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient

from linkcovery.core.config import get_config, get_config_manager
from linkcovery.core.exceptions import ConfigurationError, ImportExportError, LinKCoveryError
from linkcovery.core.utils import fetch_preview_image
from linkcovery.services.data_service import get_data_service
from linkcovery.services.link_service import LinkService, get_link_service

BASE_DIR = Path(__file__).resolve().parent
config = get_config()
cache_dir = config.get_cache_dir() / "previews"
cache_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="LinkCovery Web UI")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/cache", StaticFiles(directory=str(cache_dir)), name="cache")


@app.get("/")
async def index(request: Request, link_service: Annotated[LinkService, Depends(get_link_service)], limit: int = 30):
    links = link_service.list_links_paginated(offset=0, limit=limit)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "links": links,
            "limit": limit,
        },
    )


@app.get("/api/links")
async def list_links(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    offset: int = 0,
    limit: int = 30,
) -> JSONResponse:
    links = link_service.list_links_paginated(offset=offset, limit=limit)
    payload = [
        {
            "id": link.id,
            "url": link.url,
            "description": link.description or "",
            "tag": link.tag or "",
            "is_read": link.is_read,
            "preview_url": link.preview_url or "",
        }
        for link in links
    ]
    return JSONResponse({"links": payload})


@app.get("/api/stats")
async def api_stats(link_service: Annotated[LinkService, Depends(get_link_service)]) -> JSONResponse:
    stats_data = link_service.get_statistics()
    return JSONResponse(stats_data)


@app.get("/api/links/search")
async def api_search_links(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    q: str = "",
    tag: str = "",
    status: str = "",
    domain: str = "",
    sort: str = "newest",
    offset: int = 0,
    limit: int = 30,
) -> JSONResponse:
    is_read: bool | None = None
    if status == "read":
        is_read = True
    elif status == "unread":
        is_read = False

    links, total = link_service.search_links_paginated(
        query=q, domain=domain, tag=tag, is_read=is_read, sort=sort, offset=offset, limit=limit,
    )
    payload = [
        {
            "id": link.id,
            "url": link.url,
            "description": link.description or "",
            "tag": link.tag or "",
            "is_read": link.is_read,
            "preview_url": link.preview_url or "",
            "domain": link.domain,
            "created_at": link.created_at,
        }
        for link in links
    ]
    return JSONResponse({"links": payload, "total": total})


@app.get("/api/tags")
async def api_tags(link_service: Annotated[LinkService, Depends(get_link_service)]) -> JSONResponse:
    tags = link_service.get_all_tags()
    return JSONResponse({"tags": tags})


@app.post("/api/links/bulk-delete")
async def api_bulk_delete(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    ids: Annotated[str, Form()],
) -> JSONResponse:
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    count = link_service.bulk_delete(id_list)
    return JSONResponse({"deleted": count})


@app.post("/api/links/bulk-mark-read")
async def api_bulk_mark_read(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    ids: Annotated[str, Form()],
) -> JSONResponse:
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    count = link_service.bulk_update_read_status(id_list, is_read=True)
    return JSONResponse({"updated": count})


@app.post("/api/links/bulk-mark-unread")
async def api_bulk_mark_unread(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    ids: Annotated[str, Form()],
) -> JSONResponse:
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    count = link_service.bulk_update_read_status(id_list, is_read=False)
    return JSONResponse({"updated": count})


@app.post("/api/links/bulk-toggle")
async def api_bulk_toggle(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    ids: Annotated[str, Form()],
) -> JSONResponse:
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    count = 0
    for link_id in id_list:
        try:
            link = link_service.get_link(link_id)
            link_service.update_link(link_id=link_id, is_read=not link.is_read)
            count += 1
        except Exception:
            continue
    return JSONResponse({"updated": count})


@app.post("/links")
async def create_link(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    url: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    tag: Annotated[str, Form()] = "",
    is_read: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    link_service.add_link(url=url, description=description, tag=tag, is_read=bool(is_read))
    return RedirectResponse(url="/", status_code=303)


@app.post("/import")
async def import_links(file: UploadFile) -> RedirectResponse:
    data_service = get_data_service()
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in {".json", ".html", ".txt"}:
        msg = "Unsupported file format"
        raise ImportExportError(msg, hint="Use .json, .html, or .txt")

    temp_path: Path | None = None
    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            temp_path = Path(tmp.name)

        if suffix == ".json":
            data_service.import_from_json(temp_path)
        elif suffix == ".html":
            data_service.import_from_html(temp_path)
        else:
            data_service.import_from_txt(temp_path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

    return RedirectResponse(url="/", status_code=303)


@app.get("/export")
async def export_links() -> FileResponse:
    data_service = get_data_service()
    output_path = cache_dir / "linkcovery-export.json"
    data_service.export_to_json(output_path)
    if not output_path.exists():
        msg = "No links to export"
        raise ImportExportError(msg)
    return FileResponse(output_path, media_type="application/json", filename="linkcovery-export.json")


@app.get("/config")
async def config_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="config.html",
        context={"request": request},
    )


@app.get("/api/config")
async def api_config() -> JSONResponse:
    config_manager = get_config_manager()
    return JSONResponse(config_manager.list_all())


@app.post("/api/config/update")
async def api_config_update(
    key: Annotated[str, Form()],
    value: Annotated[str, Form()],
) -> JSONResponse:
    config_manager = get_config_manager()
    parsed_value: str | bool | int | list[str] = value
    if value.lower() in ("true", "yes", "1", "on"):
        parsed_value = True
    elif value.lower() in ("false", "no", "0", "off"):
        parsed_value = False
    elif value.isdigit():
        parsed_value = int(value)
    elif "," in value:
        parsed_value = [item.strip() for item in value.split(",")]
    try:
        config_manager.set(key, parsed_value)
        return JSONResponse({"status": "ok", "key": key, "value": parsed_value})
    except ConfigurationError as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@app.post("/api/config/reset")
async def api_config_reset() -> JSONResponse:
    config_manager = get_config_manager()
    config_manager.reset()
    return JSONResponse({"status": "ok"})


@app.get("/api/config/validate")
async def api_config_validate() -> JSONResponse:
    config_manager = get_config_manager()
    db_path = Path(config_manager.config.get_database_path())
    config_dir = config_manager.config.get_config_dir()
    issues = []
    if not db_path.exists():
        issues.append({"field": "database_path", "message": f"Database file not found at {db_path}", "type": "warning"})
    if not config_dir.exists():
        issues.append({"field": "config_dir", "message": f"Config directory not found at {config_dir}", "type": "info"})
    return JSONResponse({"valid": len(issues) == 0, "issues": issues})


@app.get("/export/markdown")
async def export_markdown() -> FileResponse:
    data_service = get_data_service()
    output_path = cache_dir / "linkcovery-export.md"
    data_service.export_to_markdown(output_path)
    if not output_path.exists():
        msg = "No links to export"
        raise ImportExportError(msg)
    return FileResponse(output_path, media_type="text/markdown", filename="linkcovery-bookmarks.md")


@app.get("/export/html")
async def export_html() -> FileResponse:
    data_service = get_data_service()
    output_path = cache_dir / "linkcovery-export.html"
    data_service.export_to_html(output_path)
    if not output_path.exists():
        msg = "No links to export"
        raise ImportExportError(msg)
    return FileResponse(output_path, media_type="text/html", filename="linkcovery-bookmarks.html")


@app.get("/links/{link_id}/edit")
async def edit_view(request: Request, link_id: int, link_service: Annotated[LinkService, Depends(get_link_service)]):
    link = link_service.get_link(link_id)
    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={
            "request": request,
            "link": link,
        },
    )


@app.post("/links/{link_id}/edit")
async def edit_link(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    link_id: int,
    url: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    tag: Annotated[str, Form()] = "",
    is_read: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    link_service.update_link(
        link_id=link_id,
        url=url,
        description=description,
        tag=tag,
        is_read=bool(is_read),
    )
    return RedirectResponse(url="/", status_code=303)


@app.post("/links/{link_id}/delete")
async def delete_link(link_id: int) -> RedirectResponse:
    link_service = get_link_service()
    link_service.delete_link(link_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/links/{link_id}/toggle")
async def toggle_read(link_id: int) -> RedirectResponse:
    link_service = get_link_service()
    link = link_service.get_link(link_id)
    link_service.update_link(link_id=link_id, is_read=not link.is_read)
    return RedirectResponse(url="/", status_code=303)


@app.get("/links/{link_id}/preview")
async def preview(link_id: int) -> JSONResponse:
    link_service = get_link_service()
    link = link_service.get_link(link_id)

    if link.preview_url:
        return JSONResponse({"preview_url": link.preview_url})

    preview_url = await fetch_preview_image(link.url)
    if not preview_url:
        link_service.update_link(link_id=link_id, preview_url="")
        return JSONResponse({"preview_url": ""})

    cache_path = await cache_preview_image(preview_url)
    if cache_path:
        local_url = f"/cache/{cache_path.name}"
        link_service.update_link(link_id=link_id, preview_url=local_url)
        return JSONResponse({"preview_url": local_url})

    link_service.update_link(link_id=link_id, preview_url=preview_url)
    return JSONResponse({"preview_url": preview_url})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(LinKCoveryError)
async def linkcovery_exception_handler(request: Request, exc: LinKCoveryError):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "message": exc.message,
            "details": exc.details,
            "hint": exc.hint,
        },
        status_code=400,
    )


async def cache_preview_image(image_url: str) -> Path | None:
    """Download image and store in cache directory."""
    try:
        digest = sha256(image_url.encode("utf-8")).hexdigest()
        parsed_path = urlparse(image_url).path
        suffix = Path(parsed_path).suffix.lower()
        if not suffix or len(suffix) > 5:
            suffix = ".jpg"
        filename = f"{digest}{suffix}"
        path = cache_dir / filename
        if path.exists():
            return path

        async with AsyncClient(timeout=10, follow_redirects=True, verify=False, http2=True) as client:
            resp = await client.get(image_url)
            resp.raise_for_status()
            content_length = int(resp.headers.get("content-length", "0") or "0")
            if content_length and content_length > 3_000_000:
                return None
            content = resp.content
            if len(content) > 3_000_000:
                return None
            path.write_bytes(content)
            return path
    except Exception:
        return None
