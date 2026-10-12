[English](allfeat.md) | [فارسی](allfeat.fa.md)

# LinkCovery: features and architecture

Version 1.7.8. Python 3.12 to 3.15, SQLite, FastAPI, [cfuicli](https://github.com/arian24b/cfui) for the CLI. The command list and options are in [README.md](README.md); this file covers the code layout and the web API.

## Layers

| Layer | Path | Role |
|---|---|---|
| CLI | `linkcovery/cli` | `app.py` (cfui app), `links.py` (add, list, search, show, edit, delete, normalize, random), `data.py` (import, export), `config.py` (config commands), `cli.py` (mark, open, stats, paths, webui, describe, ...) |
| Web UI | `linkcovery/webui` | FastAPI app, Jinja2 templates, static files |
| Services | `linkcovery/services` | `link_service.py` (link operations), `data_service.py` (import/export) |
| Core | `linkcovery/core` | `database.py` (sqlite3, WAL), `models.py` (Pydantic), `config.py`, `chrome_bookmark.py`, `utils.py`, `exceptions.py` |

The CLI and the web UI share the services and the database.

## Data

One `links` table: `id`, `url` (unique), `domain`, `description`, `tag` (comma-separated), `is_read`, `preview_url`, timestamps. Import formats: JSON, HTML, TXT, Chrome bookmarks file. Export formats: JSON, Markdown, HTML (chosen by file suffix).

## Web API (`linkcovery/webui/app.py`)

| Route | Purpose |
|---|---|
| `GET /` | main page |
| `GET /api/links`, `GET /api/links/search`, `GET /api/tags`, `GET /api/stats` | list, search, tags, statistics |
| `POST /links` | add a link |
| `GET /links/{link_id}/edit` | edit page |
| `POST /api/links/bulk-delete`, `bulk-mark-read`, `bulk-mark-unread`, `bulk-toggle` | bulk actions |
| `POST /import`, `GET /export`, `GET /export/markdown`, `GET /export/html` | import and export |
| `GET /config`, `GET /api/config`, `POST /api/config/update`, `POST /api/config/reset`, `GET /api/config/validate` | settings |

## Flows

- Add: normalize URL, fetch description (skipped with `--no-fetch`), insert; a duplicate URL is rejected.
- Search: text, `--domain`, `--tag` and read-state filters are combined with AND.
- Random: `random` picks unread links (or any with `--include-read`) and marks them read.
- Normalize: strips trailing slash and `www.`, upgrades `http` to `https`.
