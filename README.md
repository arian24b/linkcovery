<div align="center">
  <img src="https://raw.githubusercontent.com/arian24b/linkcovery/refs/heads/main/linkcovery.png" alt="LinkCovery Logo" width="400"/>
</div>

# LinkCovery - Modern Bookmark Management CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub stars](https://img.shields.io/github/stars/arian24b/linkcovery.svg?style=social&label=Star)](https://github.com/arian24b/linkcovery)
[![GitHub forks](https://img.shields.io/github/forks/arian24b/linkcovery.svg?style=social&label=Fork)](https://github.com/arian24b/linkcovery)
[![GitHub issues](https://img.shields.io/github/issues/arian24b/linkcovery.svg)](https://github.com/arian24b/linkcovery/issues)

<a href="https://www.producthunt.com/products/linkcovery?embed=true&utm_source=badge-featured&utm_medium=badge&utm_source=badge-linkcovery" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1001540&theme=light&t=1754328725689" alt="LinkCovery - The&#0032;command&#0045;line&#0032;bookmark&#0032;manager&#0032;for&#0032;developers&#0046; | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>

LinkCovery is a modern, fast, and intuitive bookmark management tool built with Python. It provides a beautiful command-line interface that makes managing, searching, and organizing your links effortless.

## 🤔 Why LinkCovery?

Browser bookmarks quickly become cluttered and inefficient. LinkCovery helps you intelligently manage and organize your links from the terminal—the place where you, as a developer, spend most of your time. With powerful search capabilities, tagging systems, and data portability, LinkCovery transforms how you interact with your saved links, making them truly useful rather than just saved.

## ✨ Features

### 🚀 Core Functionality
- **Smart Link Management**: Add, edit, delete, and organize links with ease
- **Powerful Search**: Search by URL, description, tags, domain, or read status
- **Data Portability**: Import and export your bookmarks in JSON format
- **Read Tracking**: Keep track of which links you've read
- **Rich Statistics**: Get insights into your bookmark collection

### 🏗️ Technical Excellence
- **Modern Architecture**: Clean separation of concerns with service layers
- **Type Safety**: Full Pydantic validation and type hints throughout
- **Error Handling**: Comprehensive error handling with helpful messages
- **Beautiful UI**: Rich terminal interface with tables and colors
- **Configuration**: Flexible configuration system with file-based storage
- **Cross-Platform**: Works seamlessly on macOS, Linux, and Windows

## 📦 Installation

### Prerequisites
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Install from Source
```bash
git clone https://github.com/arian24b/linkcovery.git
cd linkcovery
uv sync
```

### Install as Package
```bash
uv add linkcovery
```

## 🎯 Quick Start

After installation, you can use the `linkcovery` command directly:

### Add Your First Link
```bash
uv run linkcovery add "https://github.com/arian24b/linkcovery" \
  --desc "LinkCovery GitHub Repository" \
  --tag "github,project"
```

### List Your Links
```bash
uv run linkcovery list
```

### Search Your Bookmarks
```bash
# Search by keyword
uv run linkcovery search github

# Search by domain
uv run linkcovery search --domain github.com

# Search by tag
uv run linkcovery search --tag project
```

### Export Your Data
```bash
uv run linkcovery export my-bookmarks.json
```

### Import Bookmarks
```bash
uv run linkcovery import my-bookmarks.json
```

## 📋 CLI Reference

### Link Management
- `add <url>` - Add a new bookmark
  - `--desc, -d` - Description for the link
  - `--tag, -t` - Tag to categorize the link (can be used multiple times)
  - `--read, -r` - Mark as already read
  - `--interactive, -i` - Interactive mode with prompts
- `list` - List all bookmarks
  - `--limit, -l` - Maximum number of links to show
  - `--full` - Show full descriptions
  - `--read-only` - Show only read links
  - `--unread-only` - Show only unread links
- `search [query]` - Search bookmarks
  - `--domain` - Filter by domain
  - `--tag, -t` - Filter by tag
  - `--read-only` - Show only read links
  - `--unread-only` - Show only unread links
  - `--limit, -l` - Maximum results
  - `--interactive, -i` - Interactive selection mode
- `show <id>` - Show detailed link information
- `edit <id>` - Edit an existing link
  - `--url` - New URL
  - `--desc, -d` - New description
  - `--tag, -t` - New tags
  - `--read` - Mark as read
  - `--unread` - Mark as unread
  - `--interactive, -i` - Interactive mode with prompts
- `delete <id>` - Delete a link
  - `--force, -f` - Skip confirmation
- `mark <id>` - Mark links as read or unread
  - `--read` - Force read
  - `--unread` - Force unread
  - (If neither specified, toggles current status)
- `open <id>` - Open links in web browser
- `normalize <id>` - Normalize link URLs
  - `--all, -a` - Normalize all links
- `read-random` - Read random links from bookmarks

### Aliases
- `ls` - Alias for `list`
- `find` - Alias for `search`
- `new` - Alias for `add`
- `rm` - Alias for `delete`

### Data Management
- `export <file>` - Export links to JSON
  - `--force, -f` - Overwrite existing file
- `import <file>` - Import links from JSON or HTML

### Configuration
- `config show` - Show current configuration
- `config get <key>` - Get a specific configuration value
- `config set <key> <value>` - Set a configuration value
- `config edit` - Open config file in default editor
- `config validate` - Validate configuration
- `config reset` - Reset to default configuration

### General Commands
- `stats` - Show bookmark statistics
- `paths` - Show all LinkCovery file paths
- `version` - Show version information

## ⚙️ Configuration

LinkCovery stores its configuration in your system's config directory:
- **macOS**: `~/Library/Application Support/linkcovery/config.json`
- **Linux**: `~/.config/linkcovery/config.json`
- **Windows**: `%APPDATA%/linkcovery/config.json`

### Available Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `app_name` | "LinkCovery" | Application name |
| `version` | "1.0.0" | Application version |
| `database_path` | (auto-detected) | Custom database path |
| `default_export_format` | "json" | Default export format |
| `max_search_results` | 50 | Maximum search results |
| `allowed_extensions` | [".json"] | Allowed file extensions |
| `debug` | false | Enable debug mode |

### Examples
```bash
# Set maximum search results
uv run linkcovery config set max_search_results 100

# Enable debug mode
uv run linkcovery config set debug true

# View all settings
uv run linkcovery config show
```

## 🗄️ Database

LinkCovery uses SQLite for data storage. The database is automatically created in your system's data directory:

- **macOS**: `~/Library/Application Support/linkcovery/links.db`
- **Linux**: `~/.local/share/linkcovery/links.db`
- **Windows**: `%APPDATA%/linkcovery/links.db`

### Database Schema

The `links` table contains:
- `id` - Unique identifier (primary key)
- `url` - The bookmark URL (unique, required)
- `domain` - Extracted domain name (required)
- `description` - Optional description text
- `tag` - Associated tag for categorization
- `is_read` - Boolean read status
- `created_at` - ISO timestamp of creation
- `updated_at` - ISO timestamp of last update

## 🏗️ Project Structure

```
linkcovery/
├── main.py                         # Application entry point
├── linkcovery/
│   ├── cli/                        # Command-line interface
│   │   ├── __init__.py            # Main CLI app and routing
│   │   ├── links.py               # Link management commands
│   │   ├── config.py              # Configuration commands
│   │   ├── data.py                # Import/export commands
│   │   └── utils.py               # CLI utilities and decorators
│   ├── core/                      # Core business logic
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database service layer
│   │   ├── exceptions.py          # Custom exception classes
│   │   ├── models.py              # Pydantic and SQLAlchemy models
│   │   └── utils.py               # Core utility functions
│   └── services/                  # Business logic services
│       ├── link_service.py        # Link management business logic
│       └── data_service.py # Import/export operations
├── pyproject.toml                 # Project configuration
└── README.md                      # This file
```

## 🧪 Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/arian24b/linkcovery.git
cd linkcovery

# Install with development dependencies
uv sync --all-groups

# Install pre-commit hooks (if available)
uv run pre-commit install
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=linkcovery --cov-report=html
```

### Code Quality
```bash
# Run linting
uv run ruff check

# Format code
uv run ruff format

# Type checking
uv run mypy linkcovery
```

### Building
```bash
# Build binary
uv run python build_binary.py
```

## 📖 Examples

### Managing Links
```bash
# Add a link with description and tags
uv run linkcovery add "https://docs.python.org" \
  --desc "Official Python Documentation" \
  --tag "python,docs,reference"

# List only unread links
uv run linkcovery list --unread-only --limit 10

# Search for Python-related links
uv run linkcovery search python

# Mark a link as read
uv run linkcovery mark 5

# Mark a link as unread
uv run linkcovery mark 5 --unread

# Edit a link's description
uv run linkcovery edit 5 --desc "Updated description"
```

### Data Management
```bash
# Export all links
uv run linkcovery export my-bookmarks-$(date +%Y%m%d).json

# Import from another file
uv run linkcovery import bookmarks-backup.json

# View statistics
uv run linkcovery stats
```

### Configuration
```bash
# Increase search result limit
uv run linkcovery config set max_search_results 100

# View current configuration
uv run linkcovery config show

# Edit configuration file
uv run linkcovery config edit

# View all paths
uv run linkcovery paths

# Reset to defaults
uv run linkcovery config reset
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the project's coding standards
4. Run tests and linting (`uv run pytest && uv run ruff check`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [SQLAlchemy](https://www.sqlalchemy.org/) for database operations
- [Pydantic](https://pydantic.dev/) for data validation and settings
- [platformdirs](https://github.com/platformdirs/platformdirs) for cross-platform paths

---

**LinkCovery** - Because your bookmarks deserve better organization! 🔗✨
