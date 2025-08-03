# Makefile for LinKCovery

.PHONY: help install dev build clean test test-cov test-watch lint format type-check setup-dev binary

# Default target
help:
	@echo "LinKCovery Development Commands:"
	@echo "  install     Install production dependencies"
	@echo "  dev         Install development dependencies"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage"
	@echo "  test-watch  Run tests in watch mode"
	@echo "  build       Build Python package"
	@echo "  binary      Build standalone binary"
	@echo "  clean       Clean build artifacts"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  type-check  Run type checking with mypy"
	@echo "  setup-dev   Set up development environment"

# Install production dependencies
install:
	uv sync --no-dev

# Install development dependencies
dev:
	uv sync --all-groups

# Set up development environment
setup-dev: dev
	uv run pre-commit install || echo "Pre-commit not available"

# Run tests
test:
	uv run pytest tests/ -v

# Run tests with coverage
test-cov:
	uv run pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Run tests in watch mode (requires pytest-watch)
test-watch:
	uv run ptw tests/ --runner "pytest --tb=short"

# Build Python package
build:
	uv build

# Build standalone binary
binary: dev
	uv run python build_binary.py

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run linting
lint:
	uv run ruff check .

# Format code
format:
	uv run ruff format .

# Run type checking
type-check:
	uv run mypy app/ || echo "MyPy not configured yet"

# Fix linting issues
lint-fix:
	uv run ruff check . --fix
