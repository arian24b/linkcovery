#!/usr/bin/env python3
"""Script to update version in pyproject.toml and __init__.py files."""

import re
import sys
from pathlib import Path


def update_pyproject_toml(version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found")
        sys.exit(1)

    content = pyproject_path.read_text()

    # Update version line
    updated_content = re.sub(r'version\s*=\s*"[^"]*"', f'version = "{version}"', content)

    pyproject_path.write_text(updated_content)
    print(f"Updated version in {pyproject_path} to {version}")


def update_init_py(version: str) -> None:
    """Update version in linkcovery/__init__.py."""
    init_path = Path("linkcovery/__init__.py")

    if not init_path.exists():
        print(f"Error: {init_path} not found")
        sys.exit(1)

    content = init_path.read_text()

    # Update __version__ line
    updated_content = re.sub(r'__version__\s*=\s*"[^"]*"', f'__version__ = "{version}"', content)

    init_path.write_text(updated_content)
    print(f"Updated version in {init_path} to {version}")


def main() -> None:
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <version>")
        sys.exit(1)

    version = sys.argv[1]

    # Validate version format (basic check)
    if not re.match(r"^\d+\.\d+\.\d+.*$", version):
        print(f"Error: Invalid version format: {version}")
        sys.exit(1)

    update_pyproject_toml(version)
    update_init_py(version)

    print(f"Successfully updated version to {version}")


if __name__ == "__main__":
    main()
