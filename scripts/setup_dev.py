#!/usr/bin/env python3
"""Setup script for LinKCovery development environment."""

import subprocess
import sys


def run_command(cmd: str) -> None:
    """Run a shell command."""
    result = subprocess.run(cmd, check=False, shell=True)
    if result.returncode != 0:
        sys.exit(1)


def main() -> None:
    """Set up the development environment."""
    # Install dependencies
    run_command("uv sync --group dev")

    # Install pre-commit hooks
    run_command("uv run pre-commit install")
    run_command("uv run pre-commit install --hook-type commit-msg")

    # Set up git commit template
    run_command("git config commit.template .gitmessage")


if __name__ == "__main__":
    main()
