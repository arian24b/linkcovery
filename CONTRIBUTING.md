# Contributing to LinkCovery

Thank you for your interest in contributing to LinkCovery! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arian24b/linkcovery.git
   cd linkcovery
   ```

2. **Set up development environment**:
   ```bash
   make setup-dev
   ```

3. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   uv run pre-commit install --hook-type commit-msg
   ```

## Conventional Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for commit messages. This enables automatic semantic versioning and changelog generation.

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Examples

```bash
feat(auth): add login functionality
fix(api): resolve timeout issue
docs: update README with installation instructions
feat!: remove deprecated API endpoint
```

### Using the Helper

Use the interactive commit helper:
```bash
make commit
```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Run tests**:
   ```bash
   make test
   ```

4. **Run linting**:
   ```bash
   make lint
   ```

5. **Commit using conventional commits**:
   ```bash
   make commit
   # or manually:
   git commit -m "feat(scope): your description"
   ```

6. **Push and create a pull request**

## Release Process

Releases are automated using semantic versioning:

1. **Automatic releases**: When commits are pushed to the `main` branch, GitHub Actions automatically:
   - Analyzes commit messages
   - Determines the next version number
   - Creates a new release and tag
   - Publishes to PyPI
   - Builds and attaches binaries

2. **Manual release trigger**:
   ```bash
   make release
   ```

### Version Bumping

- `fix:` commits → PATCH version (0.1.0 → 0.1.1)
- `feat:` commits → MINOR version (0.1.0 → 0.2.0)
- `feat!:` or `BREAKING CHANGE:` → MAJOR version (0.1.0 → 1.0.0)

## Code Standards

- **Python**: Follow PEP 8, enforced by Ruff
- **Type hints**: Required for all public functions
- **Tests**: Write tests for new features and bug fixes
- **Documentation**: Update docs for user-facing changes

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run in watch mode
make test-watch
```

## Building

```bash
# Build Python package
make build

# Build binary
make binary
```

## Questions?

Feel free to open an issue for any questions about contributing!
