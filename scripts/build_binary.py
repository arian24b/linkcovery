#!/usr/bin/env python3
"""Build script for creating LinKCovery binaries using PyInstaller."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build() -> None:
    """Clean previous build artifacts."""
    for path in ["build", "dist", "*.egg-info"]:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)


def create_binary() -> None:
    """Create standalone binary using PyInstaller."""
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a one-file bundled executable
        "--name",
        "linkcovery",  # Name of the executable
        "--console",  # Console application
        "--clean",  # Clean PyInstaller cache
        "--noconfirm",  # Replace output directory without asking
        "main.py",  # Entry point
    ]

    try:
        subprocess.run(cmd, check=True)

        # Test the binary
        # test_binary()

    except subprocess.CalledProcessError:
        sys.exit(1)


def test_binary() -> None:
    """Test the created binary."""
    binary_path = Path("dist/linkcovery")

    if binary_path.exists():
        try:
            result = subprocess.run(
                [str(binary_path), "--help"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                pass
            else:
                pass
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
    else:
        pass


def main() -> None:
    """Main build function."""
    # Check if PyInstaller is available
    try:
        subprocess.run(["pyinstaller", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        sys.exit(1)

    clean_build()
    create_binary()


if __name__ == "__main__":
    main()
