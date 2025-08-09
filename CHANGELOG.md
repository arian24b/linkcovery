## [1.0.1](https://github.com/arian24b/linkcovery/compare/v1.0.0...v1.0.1) (2025-08-09)


### Bug Fixes

* Update release workflow to use semantic-release outputs for versioning and conditional binary builds ([85a1c75](https://github.com/arian24b/linkcovery/commit/85a1c75c68757a15e83dd52c0f83eb2afd8b55cb))

# 1.0.0 (2025-08-09)


### Features

* Implement automated release process with GitHub Actions and semantic versioning ([b0f6c16](https://github.com/arian24b/linkcovery/commit/b0f6c168dab457097ade38d3bcb4ed9342007c87))
* Introduce a comprehensive service layer for link management and import/export functionality ([a53b5f0](https://github.com/arian24b/linkcovery/commit/a53b5f0db764af7cf979c9faea5636992a33d18d))

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Automatic semantic versioning and release management
- GitHub Actions workflows for CI/CD
- Conventional commits support with pre-commit hooks
- Automatic PyPI publishing
- Binary builds for macOS and Linux
- Comprehensive test coverage reporting

### Changed
- Updated project structure to support automated releases
- Enhanced Makefile with new development commands

### Fixed
- Version synchronization between pyproject.toml and __init__.py

## [0.3.1] - Previous Release

### Added
- Initial release with basic bookmark management functionality
- CLI interface with Typer
- SQLAlchemy database support
- Rich terminal output
- Cross-platform compatibility
