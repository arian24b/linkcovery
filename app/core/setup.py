"""Installation and setup utilities for LinkCovery."""

from pathlib import Path

from app.core.config import config_manager
from app.core.logger import AppLogger

logger = AppLogger(__name__)


def setup_application() -> bool:
    """Setup the application with default configuration and database."""
    # Ensure config is loaded and database path is set
    config = config_manager.config

    # Create database directory if it doesn't exist
    db_path = Path(config.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Application setup complete.")
    logger.info(f"Database: {config.database_path}")
    logger.info(f"Config: {config_manager.get_config_file_path()}")

    return True


def check_setup():
    """Check if the application is properly set up."""
    try:
        config = config_manager.config
        db_path = Path(config.database_path)
        return db_path.parent.exists()
    except Exception:
        return False
