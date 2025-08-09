#!/usr/bin/env python3
"""Setup script for LinKCovery development environment."""

import subprocess
import sys


def run_command(cmd: str) -> None:
    """Run a shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Error running: {cmd}")
        sys.exit(1)


def main() -> None:
    """Set up the development environment."""
    print("Setting up LinKCovery development environment...")

    # Install dependencies
    run_command("uv sync --group dev")

    # Install pre-commit hooks
    run_command("uv run pre-commit install")
    run_command("uv run pre-commit install --hook-type commit-msg")

    # Set up git commit template
    run_command("git config commit.template .gitmessage")

    print("✅ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Set up GitHub secrets:")
    print("   - PYPI_TOKEN: Your PyPI API token")
    print("2. Start developing with conventional commits:")
    print("   - feat: new features")
    print("   - fix: bug fixes")
    print("   - docs: documentation changes")
    print("3. Push to main branch to trigger automatic release")


if __name__ == "__main__":
    main()
