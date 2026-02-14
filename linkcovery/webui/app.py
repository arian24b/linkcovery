"""FastAPI Web UI for LinkCovery."""

import hashlib
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated
from urllib.parse import urlparse

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient

from linkcovery.core.config import get_config
from linkcovery.core.exceptions import ImportExportError, LinKCoveryError
from linkcovery.core.utils import fetch_preview_image
from linkcovery.services.data_service import get_data_service
from linkcovery.services.link_service import get_link_service

BASE_DIR = Path(__file__).resolve().parent
config = get_config()
cache_dir = config.get_cache_dir() / "previews"
cache_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="LinkCovery Web UI")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/cache", StaticFiles(directory=str(cache_dir)), name="cache")


@app.get("/")
def index(request: Request, limit: int = 30):
    link_service = get_link_service()
    links = link_service.list_links_paginated(offset=0, limit=limit)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "links": links,
            "limit": limit,
        },
    )


@app.get("/api/links")
def list_links(offset: int = 0, limit: int = 30) -> JSONResponse:
    link_service = get_link_service()
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


@app.post("/links")
def create_link(
    url: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    tag: Annotated[str, Form()] = "",
    is_read: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    link_service = get_link_service()
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
def export_links() -> FileResponse:
    data_service = get_data_service()
    output_path = cache_dir / "linkcovery-export.json"
    data_service.export_to_json(output_path)
    if not output_path.exists():
        msg = "No links to export"
        raise ImportExportError(msg)
    return FileResponse(output_path, media_type="application/json", filename="linkcovery-export.json")


@app.get("/links/{link_id}/edit")
def edit_view(request: Request, link_id: int):
    link_service = get_link_service()
    link = link_service.get_link(link_id)
    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "link": link,
        },
    )


@app.post("/links/{link_id}/edit")
def edit_link(
    link_id: int,
    url: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    tag: Annotated[str, Form()] = "",
    is_read: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    link_service = get_link_service()
    link_service.update_link(
        link_id=link_id,
        url=url,
        description=description,
        tag=tag,
        is_read=bool(is_read),
    )
    return RedirectResponse(url="/", status_code=303)


@app.post("/links/{link_id}/delete")
def delete_link(link_id: int) -> RedirectResponse:
    link_service = get_link_service()
    link_service.delete_link(link_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/links/{link_id}/toggle")
def toggle_read(link_id: int) -> RedirectResponse:
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
def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(LinKCoveryError)
def linkcovery_exception_handler(request: Request, exc: LinKCoveryError):
    return templates.TemplateResponse(
        "error.html",
        {
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
        digest = hashlib.sha256(image_url.encode("utf-8")).hexdigest()
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
