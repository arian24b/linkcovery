#!/usr/bin/env python3
"""Main entry point for LinKCovery CLI application."""

from linkcovery.cli import cli_app


def run() -> None:
    cli_app()


if __name__ == "__main__":
    run()
