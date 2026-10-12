<div align="center">
  <img src="https://raw.githubusercontent.com/arian24b/linkcovery/refs/heads/main/linkcovery.png" alt="LinkCovery logo" width="400"/>
</div>

# LinkCovery

[English](README.md) | [فارسی](README.fa.md)

A bookmark manager for the terminal, with a small web UI. Add links, search them by text, domain or tag, mark what you have read, and move your data in and out as JSON, HTML or TXT.

## Install

Python 3.12 to 3.15.

```bash
uv tool install linkcovery      # or: pipx install linkcovery
linkcovery --help
```

From a clone: `uv sync && uv run linkcovery --help`.

## Quick start

```bash
linkcovery add https://github.com/arian24b/linkcovery --tag python,cli    # fetches the page description
linkcovery list --unread-only
linkcovery search python --tag cli
linkcovery mark 1                      # toggle read/unread
linkcovery export my-bookmarks.md      # .json, .md or .html, picked from the suffix
linkcovery import bookmarks.html
linkcovery webui                       # http://127.0.0.1:8000
```

## How it works

Links live in a single SQLite file (`links` table: URL, domain, description, tag, read flag, preview URL, timestamps; WAL mode). `add` fetches the page title/description with `httpx` unless you pass `--no-fetch`. The CLI (`linkcovery/cli`, built on cfuicli) and the FastAPI web UI (`linkcovery/webui`) both call the same service layer (`linkcovery/services`) over the same database, so they always show the same data.

Sample session (database in a temp file via `LINKCOVERY_DB`):

```text
$ linkcovery add https://example.com -d "Example site" -t demo --no-fetch
$ linkcovery list
ID  Status  URL                                     Description   Tag         Added
2   new     https://github.com/arian24b/linkcovery                python,cli  2026-10-12
1   new     https://example.com                     Example site  demo        2026-10-12
$ linkcovery mark 1
$ linkcovery stats
LinkCovery Statistics
   Total links: 2
   Read: 1
   Unread: 1
```

## Commands

| Command | What it does |
|---|---|
| `add URL [-d DESC] [-t TAG] [-r] [--no-fetch] [--timeout S]` (alias `new`) | save a link |
| `list [-l N] [--read-only] [--unread-only] [--full]` (alias `ls`) | show links |
| `search [QUERY] [--domain D] [-t TAG] [--read-only] [--unread-only] [-l N]` (alias `find`) | search; all filters must match |
| `show ID` | one link in detail |
| `edit ID [--url U] [-d DESC] [-t TAG] [-r] [-u]` | change a link |
| `delete ID... [-f] [-y]` (alias `rm`) | delete links, with confirmation |
| `mark ID... [-r] [-u]` | set read or unread; toggles when neither is given |
| `open ID...` | open links in the browser |
| `normalize [ID...] [-a] [-y]` | trailing slash, `http` to `https`, drop `www` |
| `describe [ID...] [-a] [-y] [-c N] [--timeout S]` | fetch missing descriptions |
| `random [-n N] [--include-read]` | pick random unread links and mark them read |
| `export [FILE] [-f] [-y]` | write all links (default `links.json`) |
| `import [FILE] [--chrome] [-y]` | read `.json`, `.html`, `.txt` or Chrome's bookmarks file |
| `stats` | totals and top domains |
| `paths` | where the config, database and data live |
| `webui [--host H] [--port P] [--reload] [--background]` | run the web UI |
| `config show\|get\|set\|reset\|edit\|validate` | settings |

Global flags: `--json` prints machine-readable output (errors become JSON on stderr) and `--no-color` turns color off. Commands that need an ID or URL ask for it when you leave it out.

## Settings

Stored in `~/.config/linkcovery/config.json` on every platform. Resolution order: environment variable, then the file, then the default. `linkcovery config show` lists each value with its source.

| Setting | Default | Meaning |
|---|---|---|
| `database_path` | auto | database file (`LINKCOVERY_DB` overrides it) |
| `default_export_format` | `json` | export format |
| `max_search_results` | `50` | search limit |
| `allowed_extensions` | `[".json"]` | accepted import extensions |
| `debug` | `false` | debug mode |

## Web UI

A small FastAPI app: add, edit and delete links, import and export, lazy-loaded list, preview images cached in `~/.cache/linkcovery/previews`. The log of a background run is `~/.local/state/linkcovery/logs/webui.log`; `linkcovery paths` prints the exact locations.

## Common commands

Built on [cfuicli](https://github.com/arian24b/cfui), so it looks and behaves like the other tools in this family.

```bash
linkcovery help [command]     # help; -h works on any command
linkcovery version            # version and git repository (also: -v)
linkcovery update [--check]   # update the tool itself; --check only compares versions
linkcovery -q ...             # quiet: no banner or notes (or LINKCOVERY_QUIET=1)
```

- A missing required option is asked for when you run the tool in a terminal. In a pipe or in CI it stops with `--flag is required. Pass --flag <value> or run interactively.` (exit code 2).
- Errors appear in a red box on stderr with a non-zero exit code. Ctrl-C exits with 130.
- Color is used only on a terminal. `NO_COLOR=1` turns it off.
- With `--json`, nothing but JSON is written to stdout.

## Development

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

Related tools: [PEM](https://github.com/arian24b/pem), [ollama-tool-cli](https://github.com/arian24b/ollamatools), [ThroneTools](https://github.com/arian24b/thronetools).

## License

MIT
