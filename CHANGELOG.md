## [1.7.5](https://github.com/arian24b/linkcovery/compare/v1.7.4...v1.7.5) (2025-08-23)


### Bug Fixes

* remove duplicate Issues URL in pyproject.toml ([a43028d](https://github.com/arian24b/linkcovery/commit/a43028d0764987e90bdfe455196505cfe9a11426))

## [1.7.4](https://github.com/arian24b/linkcovery/compare/v1.7.3...v1.7.4) (2025-08-23)


### Bug Fixes

* add workflow debugging and improve build condition syntax ([298f5d7](https://github.com/arian24b/linkcovery/commit/298f5d71756f2f0c093a20eaf8ec1b6707ff225c))

## [1.7.3](https://github.com/arian24b/linkcovery/compare/v1.7.2...v1.7.3) (2025-08-23)


### Bug Fixes

* add workflow debugging documentation ([e9d811a](https://github.com/arian24b/linkcovery/commit/e9d811ab427b3058afddea46feb9ddf2736441e7))

## [1.7.2](https://github.com/arian24b/linkcovery/compare/v1.7.1...v1.7.2) (2025-08-23)


### Bug Fixes

* use UV_PUBLISH_TOKEN environment variable for PyPI publishing ([3ae63d5](https://github.com/arian24b/linkcovery/commit/3ae63d518509c449a9fe39853335b347ceced93d))

## [1.7.1](https://github.com/arian24b/linkcovery/compare/v1.7.0...v1.7.1) (2025-08-23)


### Bug Fixes

* configure semantic-release to trigger releases for refactor commits ([e6786c6](https://github.com/arian24b/linkcovery/commit/e6786c67877025d2fb31a3808a3d4d52aad92bc0))

# [1.7.0](https://github.com/arian24b/linkcovery/compare/v1.6.0...v1.7.0) (2025-08-23)


### Features

* Enhance release workflow with version debugging and verification steps ([794c9be](https://github.com/arian24b/linkcovery/commit/794c9be0d7adaded02b2dc73f188f4e2e8f0f778))

# [1.6.0](https://github.com/arian24b/linkcovery/compare/v1.5.0...v1.6.0) (2025-08-22)


### Features

* Add command to read random links and implement random link retrieval in the service ([97e10f8](https://github.com/arian24b/linkcovery/commit/97e10f836153cf39715e9ffe4073c22bbac7469b))

# [1.5.0](https://github.com/arian24b/linkcovery/compare/v1.4.1...v1.5.0) (2025-08-21)


### Bug Fixes

* Simplify link normalization logic and improve domain extraction ([4da386a](https://github.com/arian24b/linkcovery/commit/4da386a7c4072514756de401a05e416392f1d847))


### Features

* Enhance link management with normalization features and improve command structure ([278cfed](https://github.com/arian24b/linkcovery/commit/278cfed8d9adf05e2378a40ddd1fc2e05b960ef6))

## [1.4.1](https://github.com/arian24b/linkcovery/compare/v1.4.0...v1.4.1) (2025-08-21)


### Bug Fixes

* Refactor configuration and database services; improve link handling and domain extraction ([b932a18](https://github.com/arian24b/linkcovery/commit/b932a185a8afa798d9bd49d4a7cf8d8c2cf8322f))

# [1.4.0](https://github.com/arian24b/linkcovery/compare/v1.3.0...v1.4.0) (2025-08-20)


### Features

* Enhance import functionality to support HTML files and validate input format ([d0ccab8](https://github.com/arian24b/linkcovery/commit/d0ccab85c1ad144a36f4b889cb70b0f788566396))

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
