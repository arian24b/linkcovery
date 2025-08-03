# Linkcovery CLI - Bookmark and Link Management Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Linkcovery is a powerful bookmark and link discovery tool built with Python, designed to help users efficiently manage and explore their collection of links. It provides an intuitive command-line interface (CLI) that enables developers, researchers, and avid internet users to seamlessly add, search, and organize links.

## 🚀 Features

### Core Functionality
- **Link Management**: Add, update, delete, and organize links
- **Advanced Search**: Search by domain, tags, description, and more
- **Import/Export**: Support for JSON formats
- **Tagging System**: Organize links with custom tags
- **Read Status**: Track which links you've read

### Technical Features
- **Type Safety**: Full Pydantic validation for all inputs
- **Database Migrations**: Alembic-powered schema management
- **Comprehensive Testing**: Unit and integration tests
- **Code Quality**: Pre-commit hooks with linting and formatting
- **Modular Architecture**: Clean separation of concerns with handler patterns
- **Error Handling**: Custom exception hierarchy for better debugging

## 📦 Installation

### Prerequisites
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager

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

### Initialize Database
```bash
# Create initial database migration
uv run alembic upgrade head
```

### Add Your First Link
```bash
uv run linkcovery link create
  --url "https://github.com/arian24b/linkcovery"
  --domain "github.com"
  --description "LinKCovery GitHub Repository"
  --tag "github" --tag "project"
```

### List Your Links
```bash
uv run linkcovery link list
```

### Search Links
```bash
# Search by domain
uv run linkcovery link search --domain "github.com"

# Search by tag
uv run linkcovery link search --tag "project"

# Search by description
uv run linkcovery link search --description "repository"
```

### Export Links
```bash
# Export to JSON
uv run linkcovery import-export export --format json --output links.json
```

### Import Links
```bash
# Import from JSON
uv run linkcovery import-export import --file links.json --format json
```

## 🛠️ CLI Commands

### Link Management
- `linkcovery link create` - Add a new link
- `linkcovery link list` - List all links
- `linkcovery link search` - Search links by various criteria
- `linkcovery link update` - Update an existing link
- `linkcovery link delete` - Delete a link
- `linkcovery link mark-read` - Mark a link as read

### Import/Export
- `linkcovery import-export import` - Import links from file
- `linkcovery import-export export` - Export links to file

### Configuration
- `linkcovery config get` - Get configuration value
- `linkcovery config set` - Set configuration value
- `linkcovery config list` - List all configuration
- `linkcovery config reset` - Reset to defaults

### Utility
- `linkcovery version` - Show version information

## 📁 Project Structure

```
linkcovery/
├── linkcovery/
│   ├── cli/                 # CLI interface
│   │   ├── commands.py      # CLI command definitions
│   │   ├── handlers.py      # CLI command handlers
│   │   └── __init__.py      # CLI app initialization
│   └── core/                # Core functionality
│       ├── database/        # Database layer
│       │   ├── models.py    # SQLAlchemy models
│       │   ├── crud.py      # CRUD operations
│       │   ├── repositories.py  # Repository pattern
│       │   └── session_manager.py  # Database session management
│       ├── exceptions.py    # Custom exceptions
│       ├── logger.py        # Logging configuration
│       ├── settings.py      # Configuration management
│       └── utils.py         # Utility functions
├── main.py                  # Entry point
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## 🧪 Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/arian24b/linkcovery.git
cd linkcovery

# Install with development dependencies
uv sync --group dev --group test --group lint

# Install pre-commit hooks
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
uv run pre-commit run --all-files

# Type checking
uv run mypy linkcovery
```

### Building
```bash
# Build binary
uv run python build_binary.py
```

## 🗄️ Database

LinKCovery uses SQLite as its database backend. The database file is automatically created in your system's data directory:

- **macOS**: `~/Library/Application Support/linkcovery/app.db`
- **Linux**: `~/.local/share/linkcovery/app.db`
- **Windows**: `%APPDATA%\linkcovery\app.db`

### Database Schema

The main `links` table contains:
- `id` - Unique identifier
- `url` - The link URL (required)
- `domain` - Domain name (required)
- `description` - Optional description
- `tag` - Associated tag (required)
- `is_read` - Read status (boolean)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## 🔧 Configuration

Configuration is stored in JSON format in your system's config directory. You can manage it using the `config` commands:

```bash
# View current configuration
uv run linkcovery config list

# Set maximum search results
uv run linkcovery config set max_search_results 20

# Enable debug mode
uv run linkcovery config set debug true
```

Default configuration values:
- `database_path`: Auto-detected system data directory
- `debug`: `false`
- `allowed_extensions`: `[".json"]`
- `default_export_format`: `"json"`
- `max_search_results`: `10`
- `app_name`: `"LinkCovery"`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`uv run pytest && uv run pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI interface
- Uses [SQLAlchemy](https://www.sqlalchemy.org/) for database operations
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [Pydantic](https://pydantic.dev/) for data validation
