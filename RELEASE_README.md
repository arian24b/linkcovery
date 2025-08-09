# LinkCovery - Automated Release Setup

This project is configured with automated versioning, tagging, and publishing.

## Quick Setup

1. **Set up development environment**:
   ```bash
   python setup_dev.py
   ```

2. **Configure GitHub secrets** (in your repository settings):
   - `PYPI_TOKEN`: Your PyPI API token for publishing

## How It Works

### Automatic Releases
- Push commits to `main` branch
- GitHub Actions automatically:
  - Analyzes commit messages
  - Determines version bump (patch/minor/major)
  - Creates git tag and GitHub release
  - Publishes to PyPI
  - Builds binaries for macOS and Linux

### Conventional Commits
Use these commit message formats:
- `feat: add new feature` → minor version bump
- `fix: resolve bug` → patch version bump
- `feat!: breaking change` → major version bump

### Pre-commit Hooks
Automatically enforces:
- Code formatting with Ruff
- Conventional commit messages

## Development Commands

```bash
# Install dependencies
uv sync

# Install with build tools
uv sync --group build

# Build package
uv build

# Build binary
uv run python build_binary.py

# Format code
uv run ruff format .

# Lint code
uv run ruff check . --fix
```

## Manual Release
Simply push to main with conventional commits - releases are fully automated!
