# Contributing to LinKCovery

Thank you for your interest in contributing to LinKCovery! This document provides guidelines and information for contributors.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/linkcovery.git
   cd linkcovery
   ```

2. **Set up Environment**
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv sync --group dev

   # Install pre-commit hooks
   uv run pre-commit install
   ```

3. **Initialize Database**
   ```bash
   uv run alembic upgrade head
   ```

4. **Verify Setup**
   ```bash
   # Run tests
   uv run pytest

   # Run the CLI
   uv run linkcovery --help
   ```

### Project Structure

```
linkcovery/
├── app/
│   ├── cli/                    # CLI commands and interface
│   │   ├── commands/          # Typer command groups
│   │   └── handlers/          # Business logic handlers
│   ├── core/                  # Core application logic
│   │   ├── config/           # Configuration management
│   │   ├── database/         # Database models and services
│   │   ├── exceptions/       # Custom exception hierarchy
│   │   ├── interfaces/       # Service protocols
│   │   ├── services/         # Business services
│   │   └── validation/       # Pydantic schemas
│   └── __init__.py
├── tests/
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── conftest.py          # Test configuration
├── alembic/                 # Database migrations
├── docs/                    # Documentation
└── README.md
```

## 🛠️ Development Workflow

### 1. Choose an Issue

- Look for issues labeled `good first issue` for newcomers
- Check `help wanted` for areas where contributions are especially welcome
- Feel free to create new issues for bugs or feature requests

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-fix-name
```

### 3. Make Changes

Follow these guidelines:

#### Code Style
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

#### Architecture Guidelines
- Follow the existing patterns (handlers, services, repositories)
- Add business logic to handlers, not CLI commands
- Use Pydantic schemas for all input validation
- Create custom exceptions for specific error cases
- Add interfaces/protocols for new services

#### Example Code Structure
```python
# Handler example
class CreateItemHandler(BaseCommandHandler):
    \"\"\"Handler for creating new items\"\"\"

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)

    def execute(self, item_data: dict[str, Any]) -> dict[str, Any]:
        \"\"\"Create a new item with validation\"\"\"
        with self.db_manager.get_session() as session:
            # Business logic here
            pass

# Validation schema example
class CreateItemRequest(BaseModel):
    \"\"\"Schema for item creation requests\"\"\"
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Example Item",
                "description": "An example description"
            }
        }
```

### 4. Testing

#### Write Tests
Every contribution should include appropriate tests:

```python
# Unit test example
def test_create_item_success(self, item_service, sample_item_data):
    \"\"\"Test successful item creation\"\"\"
    item = item_service.create_item(sample_item_data)
    assert item.name == sample_item_data["name"]
    assert item.id is not None

# Integration test example
def test_item_create_cli_integration(self):
    \"\"\"Test item creation through CLI\"\"\"
    runner = CliRunner()
    result = runner.invoke(
        item_app,
        ["create", "--name", "Test Item", "--description", "Test description"]
    )
    assert result.exit_code == 0
    assert "Test Item" in result.stdout
```

#### Run Tests
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_item_service.py

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run integration tests only
uv run pytest tests/integration/
```

### 5. Quality Checks

Before committing, ensure your code passes all quality checks:

```bash
# Formatting and linting (pre-commit will run these automatically)
uv run ruff check
uv run ruff format

# Type checking
uv run mypy app/

# Run all pre-commit hooks
uv run pre-commit run --all-files

# Test database migrations
uv run alembic check
```

### 6. Commit and Push

```bash
# Stage your changes
git add .

# Commit with a meaningful message
git commit -m "feat: add new item management functionality"

# Push to your fork
git push origin feature/your-feature-name
```

#### Commit Message Format
Use conventional commits format:

- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` formatting, missing semicolons, etc.
- `refactor:` code changes that neither fix bugs nor add features
- `test:` adding or updating tests
- `chore:` maintenance tasks

Examples:
```
feat: add search functionality to link management
fix: resolve database connection timeout issue
docs: update API documentation for user endpoints
test: add integration tests for import/export functionality
```

### 7. Create Pull Request

1. Go to the GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template with:
   - Clear description of changes
   - Link to related issues
   - Screenshots if applicable
   - Testing notes

## 📝 Documentation

### Writing Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions and classes
- Update CLI help text for new commands
- Add examples for new features

### Documentation Standards

```python
def create_user(self, user_data: dict[str, Any]) -> User:
    \"\"\"Create a new user account.

    Args:
        user_data: Dictionary containing user information including
                  'name' and 'email' fields.

    Returns:
        User: The created user object with assigned ID.

    Raises:
        EntityAlreadyExistsError: If user with email already exists.
        ValidationError: If user_data is invalid.

    Example:
        >>> user_data = {"name": "John Doe", "email": "john@example.com"}
        >>> user = service.create_user(user_data)
        >>> print(user.id)
        1
    \"\"\"
```

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions/methods
   - Mock external dependencies
   - Fast execution
   - High coverage

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use real database (in-memory)
   - Test CLI commands end-to-end

3. **Handler Tests** (`tests/unit/test_handlers.py`)
   - Test business logic handlers
   - Validate error handling
   - Test success and failure paths

### Testing Best Practices

- Write tests before implementing features (TDD)
- Use descriptive test names
- Test both success and error cases
- Use fixtures for common test data
- Keep tests independent and isolated

## 🚀 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Creating Releases

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Publish to PyPI (maintainers only)

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - OS and version
   - Python version
   - LinKCovery version
   - Command that caused the issue

2. **Steps to Reproduce**
   - Exact commands run
   - Expected behavior
   - Actual behavior

3. **Additional Context**
   - Error messages
   - Log files
   - Screenshots if applicable

## 💡 Feature Requests

For feature requests, please provide:

1. **Problem Description**
   - What problem does this solve?
   - Current workarounds

2. **Proposed Solution**
   - Detailed description
   - Alternative solutions considered

3. **Additional Context**
   - Use cases
   - Similar features in other tools

## ❓ Questions and Support

- **GitHub Discussions**: For questions and general discussions
- **GitHub Issues**: For bug reports and feature requests
- **Email**: arian24b@example.com for direct contact

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributor graphs

Thank you for contributing to LinKCovery! 🚀
