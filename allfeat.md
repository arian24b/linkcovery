🔗 LinkCovery — Full Features & Flows Analysis
Version: 1.7.8 | Stack: Python (Typer CLI + FastAPI Web UI + SQLite) | Architecture: 3-layer (CLI → Services → Core/Database)
🏗️ Architecture Overview
CLI Layer (Typer)          Services Layer            Core Layer
─────────────────          ─────────────            ──────────
cli/__init__.py             services/                 core/
  cli.py (main app)          link_service.py          database.py (SQLite)
  links.py (CRUD cmds)       data_service.py          models.py (Pydantic)
  config.py (config cmds)                              config.py
  data.py (import/export)                              utils.py
                                                      exceptions.py
                                                      chrome_bookmark.py
webui/app.py (FastAPI)      ────── shares ──────►   same core/services
1️⃣ ALL SINGLE FEATURES (Atomic Operations)
Each row = one atomic action a user can trigger.
📌 Link Management (CLI)
#	Feature	Command	Options / Details	Code Location
1	Add link	add <url>	--desc, --tag, --read, --no-fetch, --timeout	links.py:14-46
2	List links	list / ls	--limit, --full, --read-only, --unread-only	links.py:48-107
3	Search links	search <query> / find	--domain, --tag, --read-only, --unread-only, --limit (AND logic across filters)	links.py:110-185
4	Show link detail	show <id>	Displays: URL, Domain, Description, Tag, Read status, Created/Updated timestamps	links.py:188-207
5	Edit link	edit <id>	--url, --desc, --tag, --read, --unread	links.py:210-249
6	Delete link	delete <id> / rm	--force (skip confirm); supports multiple IDs	links.py:252-277
7	Mark link(s)	mark <ids>	--read / --unread (toggle if unspecified); batch supported	cli.py:145-184
8	Open in browser	open <ids>	Opens multiple links in default browser sequentially	cli.py:187-207
9	Normalize URL	normalize <id>	Strips trailing /, www., converts http→https; --all for all links	links.py:280-318
10	Read random	read-random	--number (default 5), --include-read; marks unread as read	links.py:321-361
11	Show stats	stats	Total links, Read, Unread, Top 5 domains	cli.py:91-106
12	Show paths	paths	Config file, Database, Data directory + size + modified date	cli.py:109-142
13	Show version	version	Banner + version string	cli.py:247-250
⚙️ Configuration (CLI)
#	Feature	Command	Details	Code Location
14	Show config	config show	Table of all settings	config.py:16-43
15	Get config key	config get <key>	Single value lookup	config.py:46-58
16	Set config key	config set <key> <value>	Auto-parses bool/int/list types	config.py:61-115
17	Edit config file	config edit	Opens in OS default editor	config.py:136-159
18	Validate config	config validate	Checks DB path + config dir	config.py:162-189
19	Reset config	config reset	Restores defaults (requires confirm)	config.py:118-133
📦 Data Management (CLI)
#	Feature	Command	Details	Code Location
20	Export to JSON	export <file>	--force to overwrite	data.py:13-35
21	Import from JSON	import <file>	Skips duplicates, progress bar, auto-fetches descriptions	data.py:37-68, data_service.py:47-98
22	Import from HTML	import file.html	Parses Chrome-style bookmark HTML	data_service.py:145-185
23	Import from TXT	import file.txt	One URL per line; # comments ignored	data_service.py:100-143
🌐 Web UI (FastAPI)
#	Feature	Route / Action	Details	Code Location
24	Launch Web UI	webui	--host, --port, --reload, --background	cli.py:57-88
25	Index page	GET /	First page of links via template	app.py:33-45
26	API: List links	GET /api/links	Paginated: offset, limit	app.py:48-66
27	API: Search links	GET /api/links/search	q, tag, status, domain, sort, offset, limit	app.py:75-108
28	API: Get stats	GET /api/stats	Total/read/unread/top_domains	app.py:69-72
29	API: List tags	GET /api/tags	All tags with counts	app.py:111-114
30	API: Bulk delete	POST /api/links/bulk-delete	Comma-separated IDs	app.py:117-124
31	API: Bulk mark read	POST /api/links/bulk-mark-read	Comma-separated IDs	app.py:127-134
32	API: Bulk mark unread	POST /api/links/bulk-mark-unread	Comma-separated IDs	app.py:137-144
33	API: Bulk toggle	POST /api/links/bulk-toggle	Toggles read/unread per link	app.py:147-161
34	Create link	POST /links	Form: url, description, tag, is_read	app.py:164-173
35	Edit link page	GET /links/{id}/edit	Form pre-filled with link data	app.py:294-304
36	Edit link submit	POST /links/{id}/edit	Updates URL, desc, tag, read status	app.py:307-323
37	Delete link	POST /links/{id}/delete	Deletes and redirects to /	app.py:326-330
38	Toggle read	POST /links/{id}/toggle	Flips read/unread	app.py:333-338
39	Fetch preview	GET /links/{id}/preview	Fetches og:image, caches locally (SHA256-keyed, max 3MB)	app.py:341-361
40	Import via upload	POST /import	File upload (JSON/HTML/TXT)	app.py:176-201
41	Export JSON	GET /export	Downloads linkcovery-export.json	app.py:204-212
42	Export Markdown	GET /export/markdown	Downloads linkcovery-bookmarks.md	app.py:272-280
43	Export HTML	GET /export/html	Downloads linkcovery-bookmarks.html (styled)	app.py:283-291
44	Config page	GET /config	Web UI for config management	app.py:215-221
45	API: Get config	GET /api/config	All settings as JSON	app.py:224-227
46	API: Update config	POST /api/config/update	Parses bool/int/list/string	app.py:230-249
47	API: Reset config	POST /api/config/reset	Restores defaults	app.py:252-256
48	API: Validate config	GET /api/config/validate	Checks DB + config dir	app.py:259-269
49	Error page	Error handler	error.html with message, details, hint	app.py:369-381
♻️ Background / Internal Services
#	Feature	Details	Code Location
50	Auto-fetch description	On add, HTML-parses <meta name="description"> from URL (async via httpx)	utils.py:118-161
51	Auto-fetch preview image	HTML-parses <meta property="og:image"> or first <img>, caches locally	utils.py:164-184, app.py:384-409
52	URL normalization	Removes www., trailing /, http→https	utils.py:66-87
53	Domain extraction	Parses netloc from URL, strips www.	utils.py:57-63
54	Chrome HTML parser	Parses <a href="..."> from Chrome-style bookmark exports	chrome_bookmark.py
55	Bulk delete	Deletes multiple links, returns count	link_service.py:135-144
56	Bulk update read status	Batch mark read/unread	link_service.py:146-155
57	Get all tags	With link counts, sorted by frequency	database.py:383-398
58	Database init	Auto-creates links table + 6 indexes on first run	database.py:67-90
59	Config persistence	JSON file at ~/.config/linkcovery/config.json	config.py:93-161
60	Error handling decorator	Catches all exceptions, shows hint, supports LINKCOVERY_DEBUG	utils.py:18-43
🔌 CLI Aliases
#	Alias	Maps To
61	ls → list	cli.py:211-217
62	find → search	cli.py:220-226
63	new → add	cli.py:229-235
64	rm → delete	cli.py:238-244
2️⃣ ALL FLOWS (Multi-Step Processes)
Each flow = a sequence of features/actions that together accomplish a user goal.
Flow A: 📥 Add a Bookmark (CLI)
User:  linkcovery add <url> [--desc "..." --tag "t" --read --no-fetch]
   │
   ├─► [links.py:add] LinkService.add_link() called
   │     ├─► Pydantic validates URL format (must have http:// or https://)
   │     ├─► If --no-fetch is NOT set: async fetch_description() called
   │     │     ├─► HTTP GET to URL (httpx, follow_redirects, http2)
   │     │     ├─► HTMLParser extracts <meta name="description" content="...">
   │     │     └─► Returns description or "" on failure
   │     ├─► DatabaseService.create_link()
   │     │     ├─► Checks duplicate URL → raises LinkAlreadyExistsError
   │     │     ├─► Extracts domain from URL
   │     │     ├─► INSERT INTO links with timestamps
   │     │     └─► Returns Link object with generated ID
   │     └─► Console prints "✅ Added link #N"
   └─► User sees confirmation
Flow B: 🔍 Search + Filter Bookmarks
User:  linkcovery search <query> [--domain X --tag Y --read-only --limit N]
   │
   ├─► [links.py:search] LinkService.search_links(query, domain, tag, is_read, limit)
   │     ├─► Builds LinkFilter model with AND logic
   │     ├─► DatabaseService.search_links()
   │     │     ├─► Dynamic SQL: "SELECT * FROM links WHERE 1=1"
   │     │     ├─► Appends LIKE clauses per filter
   │     │     ├─► ORDER BY created_at DESC LIMIT ?
   │     │     └─► Returns filtered Link list
   │     └─► Renders Rich Table: ID | Status | URL | Description | Tag
   └─► User sees results or "No matches found"
Flow C: ✏️ Edit a Bookmark (CLI)
User:  linkcovery edit <id> --url "..." --desc "..." --tag "..."
   │
   ├─► [links.py:edit] LinkService.update_link(id, url, desc, tag, is_read)
   │     ├─► DatabaseService.update_link()
   │     │     ├─► GET existing link (raises LinkNotFoundError if missing)
   │     │     ├─► Builds dynamic UPDATE SET clause from non-None fields
   │     │     ├─► If URL changed → re-extracts domain
   │     │     ├─► Sets updated_at = now
   │     │     └─► Returns updated Link
   │     └─► Prints "✅ Updated link #N"
   └─► User sees confirmation / error
Flow D: 📂 Import Bookmarks (CLI)
User:  linkcovery import <file.json|.html|.txt>
   │
   ├─► [data.py:import_data]
   │     ├─► Checks file exists → exit if not
   │     ├─► Confirms with user (Y/n)
   │     └─► Routes by extension:
   │           ├─► .json → DataService.import_from_json()
   │           │     ├─► Reads JSON array of link objects
   │           │     ├─► Shows Progress bar
   │           │     ├─► For each: checks exists? → skip; else add_link()
   │           │     └─► Reports added/failed counts + failures
   │           ├─► .html → DataService.import_from_html()
   │           │     ├─► ChromeBookmark.extractor() parses <a href> tags
   │           │     ├─► Same loop as JSON + auto-fetches descriptions
   │           │     └─► Progress bar + report
   │           └─► .txt → DataService.import_from_txt()
   │                 ├─► Reads lines, strips, skips # comments
   │                 └─► Same loop (no auto-fetch)
   └─► User sees import summary
Flow E: 💾 Export Bookmarks (CLI)
User:  linkcovery export <file.json>
   │
   ├─► [data.py:export]
   │     ├─► Checks if file exists → confirm overwrite unless --force
   │     ├─► DataService.export_to_json()
   │     │     ├─► LinkService.list_all_links() → all links
   │     │     ├─► Converts each Link → LinkExport (Pydantic model)
   │     │     └─► JSON dump with indent=2 to file
   │     └─► "✅ Exported N links to file"
   └─► File written to disk
Flow F: 🌐 Web UI Session (Full User Journey)
User:  linkcovery webui [--host 0.0.0.0 --port 8080 --background]
   │
   ├─► [cli.py:webui] Options:
   │     ├─► --background: spawns uvicorn subprocess, logs to file, opens browser
   │     └─► foreground: runs uvicorn directly, opens browser
   │
   └─► Browser opens → [index.html] Alpine.js SPA:
         │
         ├─► On load (init()):
         │     ├─► fetchStats() → GET /api/stats (total/read/unread/domains)
         │     ├─► fetchTags() → GET /api/tags (tag dropdown)
         │     └─► fetchLinks() → GET /api/links/search?offset=0&limit=30
         │
         ├─► **Add link** (form + POST /links)
         │     ├─► FormData(url, desc, tag, is_read)
         │     ├─► Server adds via LinkService
         │     └─► Refetches stats + tags + links
         │
         ├─► **Search** (input + debounce 300ms):
         │     ├─► GET /api/links/search?q=...&tag=...&status=...&sort=...
         │     ├─► Resets to page 1
         │     └─► Re-renders card list
         │
         ├─► **Filter pills**: All | Unread | Read → same search API
         ├─► **Sort**: Newest | Oldest | Domain | Read status
         ├─► **Pagination**: prev/next + page numbers + scroll-to-top
         │
         ├─► **Toggle read** → POST /links/{id}/toggle → fetchLinks()
         ├─► **Edit link** → GET /links/{id}/edit → [edit.html]
         │     ├─► Form pre-filled with current link data
         │     ├─► Submit → POST /links/{id}/edit → redirect to /
         │     └─► Delete button with modal confirmation
         │
         ├─► **Delete link** → modal confirm → POST /links/{id}/delete → refetch
         │
         ├─► **Bulk actions** (checkboxes → fixed bottom bar):
         │     ├─► Select multiple cards
         │     ├─► Actions: Mark Read | Mark Unread | Toggle | Delete
         │     ├─► Each: POST to /api/links/bulk-{action} with comma-separated IDs
         │     └─► Refetches links + stats + tags
         │
         ├─► **Preview images**:
         │     ├─► GET /links/{id}/preview on card load
         │     ├─► Fetches og:image, caches with SHA256 hash
         │     └─► Serves from /cache/{hash}{ext}
         │
         ├─► **Export**: links to JSON / Markdown / HTML download
         ├─► **Import**: file upload → POST /import → redirect
         │
         ├─► **Config page** → [config.html]:
         │     ├─► GET /api/config → editable fields
         │     ├─► Boolean: toggle switch, Number: input, List: comma-separated
         │     ├─► Save per-field → POST /api/config/update
         │     ├─► Validate button → GET /api/config/validate
         │     └─► Reset → POST /api/config/reset
         │
         ├─► **Dark mode** toggle (localStorage persisted)
         ├─► **Keyboard shortcuts**:
         │     ├── s → focus search
         │     ├── n → focus "Add link" first input
         │     ├── d → toggle dark mode
         │     ├── ? → show shortcuts modal
         │     └── Esc → close modals
         │
         └─► **Toast notifications** (auto-dismiss after 3s)
Flow G: 🔄 Mark + Read-Random Flow
User:  linkcovery read-random --number 10
   │
   ├─► [links.py:read_random]
   │     ├─► LinkService.get_random_links(10, unread_only=True)
   │     │     └─► SQL: "SELECT * FROM links WHERE is_read=0 ORDER BY RANDOM() LIMIT 10"
   │     ├─► For each random link:
   │     │     ├─► Prints URL + description
   │     │     ├─► If unread: LinkService.mark_as_read(id) → prints ✅
   │     │     └─► If already read: prints 📖 Already read
   │     └─► Supports --include-read to include already-read links
   └─► User sees N random links, unread ones marked as read
Flow H: 🔗 URL Normalization Flow
User:  linkcovery normalize --all
   │
   ├─► [links.py:normalize]
   │     ├─► LinkService.normalize_all_links()
   │     │     ├─► Iterates all links
   │     │     ├─► normalize_url() each:
   │     │     │     ├─► Strips www. from hostname
   │     │     │     ├─► Ensures https:// scheme
   │     │     │     ├─► Removes trailing slash from path
   │     │     │     └─► Preserves per-userinfo, query, fragment
   │     │     ├─► Updates link via DatabaseService.update_link()
   │     │     └─► Skips failures silently
   │     └─► Reports total normalized count + details
   └─› All URLs normalized in-place
Flow I: ⚙️ Configuration Management Flow
User:  linkcovery config set max_search_results 100
   │
   ├─► [config.py:set]
   │     ├─► Shows available keys if no arguments
   │     ├─► ConfigManager.set(key, value)
   │     │     ├─► Auto-type parsing: "true"/"false"→bool, digits→int, commas→list
   │     │     ├─► Validates key exists on AppConfig model
   │     │     ├─► Creates new AppConfig with updated value
   │     │     └─► Saves to ~/.config/linkcovery/config.json
   │     └─► Prints "✅ Set key = value"
   └─› Config persisted and immediately active
Flow J: 🖼️ Preview Image Caching Flow (Web UI)
User views a link card in Web UI
   │
   ├─► JS calls GET /links/{id}/preview
   ├─► [app.py:preview]
   │     ├─► If link.preview_url exists → return it (cached)
   │     ├─► Else: fetch_preview_image(url)
   │     │     ├─► HTTP GET to URL
   │     │     ├─► HTMLParser extracts <meta property="og:image" content="...">
   │     │     ├─► Fallback: first <img> src
   │     │     └─► Returns absolute URL
   │     ├─► If image URL found:
   │     │     ├─► cache_preview_image(url)
   │     │     │     ├─► SHA256 hash → filename
   │     │     │     ├─► Checks local cache → return if exists
   │     │     │     ├─► Downloads image (max 3MB)
   │     │     │     └─► Writes to ~/.cache/linkcovery/previews/
   │     │     └─► Saves cache path to link.preview_url
   │     └─► Returns local /cache/{hash}.{ext} or original URL
   └─► Image displays in card thumbnail
3️⃣ EXCEPTION HANDLING (Custom Errors)
Error	When Raised	Hint
LinkNotFoundError	Get/Update/Delete nonexistent ID	"Use 'linkcovery list' to see all available links"
LinkAlreadyExistsError	Add URL that's already in DB	"Use 'linkcovery edit <id>' to update existing link"
ConfigurationError	Invalid config key/parse failure	"Use 'linkcovery config show' to see current configuration"
ImportExportError	File I/O failures, unsupported format	"Check file permissions and format"
DatabaseError	SQLite errors	—
ValidationError	Pydantic validation failures	—
4️⃣ DATABASE SCHEMA
links (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  url         TEXT UNIQUE NOT NULL,
  domain      TEXT NOT NULL,
  description TEXT DEFAULT '',
  tag         TEXT DEFAULT '',
  is_read     INTEGER DEFAULT 0,       -- 0=unread, 1=read
  preview_url TEXT DEFAULT '',
  created_at  TEXT NOT NULL,            -- ISO 8601
  updated_at  TEXT NOT NULL             -- ISO 8601
)
-- Indexes: domain, tag, is_read, created_at, (domain,is_read), (tag,is_read)
-- Pragmas: WAL mode, NORMAL sync, 10MB cache, MEMORY temp, 256MB mmap
5️⃣ CONFIGURATION SETTINGS
Key	Type	Default	Description
app_name	string	"LinkCovery"	Display name
version	string	"1.7.8"	Version
database_path	string|null	~/.linkcovery/links.db	Custom DB path (env: LINKCOVERY_DB)
default_export_format	string	"json"	Export format
max_search_results	int	50	Max search results
allowed_extensions	list[str]	[".json"]	Allowed import formats
debug	bool	false	Debug mode
Total: 64 individual features + 10 distinct flows. Want me to dive deeper into any specific flow or feature?
