# [1.3.0](https://github.com/arian24b/linkcovery/compare/v1.2.0...v1.3.0) (2025-08-20)


### Features

* Add main.py to initialize the linkcovery CLI application ([16ab6ba](https://github.com/arian24b/linkcovery/commit/16ab6ba2bce335b8bf7a632096a71de771fa925c))

# [1.2.0](https://github.com/arian24b/linkcovery/compare/v1.1.0...v1.2.0) (2025-08-19)


### Bug Fixes

* Update entry point for linkcovery CLI script ([4e82c76](https://github.com/arian24b/linkcovery/commit/4e82c766d4f668e37139a1c514f2df96524ab02c))


### Features

* Implement database migration script to add performance indexes and optimize queries ([f9ea296](https://github.com/arian24b/linkcovery/commit/f9ea296bc1260801a850e9e1438c18c29a8ad7bd))

# [1.1.0](https://github.com/arian24b/linkcovery/compare/v1.0.2...v1.1.0) (2025-08-14)


### Features

* Add script to automate link addition from JSON file ([6d2cf99](https://github.com/arian24b/linkcovery/commit/6d2cf99a6220d90db3bcef0fbe8358a3f895ccc9))
* Enhance link addition with automatic description and tags fetching ([4f954fb](https://github.com/arian24b/linkcovery/commit/4f954fbea330b2d52083322abc5c0b4f46aca53a))

## [1.0.2](https://github.com/arian24b/linkcovery/compare/v1.0.1...v1.0.2) (2025-08-09)


### Bug Fixes

* Remove conditional checks for new release publication in publish and build-binaries jobs ([ee31f83](https://github.com/arian24b/linkcovery/commit/ee31f83b77e4a0f131e02d3eea0c550d24f0c0e0))

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
