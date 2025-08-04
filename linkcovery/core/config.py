"""Simple configuration for LinKCovery."""

import os
from pathlib import Path


class Config:
    """Simple configuration class."""

    def __init__(self) -> None:
        # Application info
        self.APP_NAME = "LinkCovery"
        self.VERSION = "0.3.1"

        # Database configuration
        self.DATABASE_PATH = self._get_database_path()

        # Export/Import settings
        self.DEFAULT_EXPORT_FORMAT = "json"
        self.MAX_SEARCH_RESULTS = 50

        # Debug mode
        self.DEBUG = os.getenv("LINKCOVERY_DEBUG", "false").lower() == "true"

    def _get_database_path(self) -> str:
        """Get the database path with fallback options."""
        # Try environment variable first
        db_path = os.getenv("LINKCOVERY_DB")
        if db_path:
            return db_path

        # Try platformdirs if available
        try:
            from platformdirs import user_data_dir

            data_dir = Path(user_data_dir("linkcovery"))
            data_dir.mkdir(parents=True, exist_ok=True)
            return str(data_dir / "links.db")
        except ImportError:
            # Fallback to home directory
            data_dir = Path.home() / ".linkcovery"
            data_dir.mkdir(parents=True, exist_ok=True)
            return str(data_dir / "links.db")


# Global configuration instance
config = Config()
