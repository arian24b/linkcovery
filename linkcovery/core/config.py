"""Configuration management for LinKCovery."""

from json import dump
from json import load as jload
from os import getenv
from pathlib import Path

from pydantic import BaseModel

from linkcovery import __version__ as linkcovery_version
from linkcovery.core.exceptions import ConfigurationError


class AppConfig(BaseModel):
    """Application configuration model."""

    # Application info
    app_name: str = "LinKCovery"
    version: str = linkcovery_version

    # Database configuration
    database_path: str | None = None

    # Export/Import settings
    default_export_format: str = "json"
    max_search_results: int = 50
    allowed_extensions: list[str] = [".json"]

    # Debug and development
    debug: bool = False

    # Cache for expensive operations
    _cached_db_path: str | None = None
    _cached_config_dir: Path | None = None

    def get_database_path(self) -> str:
        """Get the database path with fallback options (cached)."""
        if self._cached_db_path:
            return self._cached_db_path

        if self.database_path:
            self._cached_db_path = self.database_path
            return self._cached_db_path

        # Try environment variable first
        if db_path := getenv("LINKCOVERY_DB"):
            self._cached_db_path = db_path
            return self._cached_db_path

        # Try platformdirs if available
        try:
            from platformdirs import user_data_dir

            data_dir = Path(user_data_dir("linkcovery"))
            data_dir.mkdir(parents=True, exist_ok=True)
            self._cached_db_path = str(data_dir / "links.db")
        except ImportError:
            # Fallback to home directory
            data_dir = Path.home() / ".linkcovery"
            data_dir.mkdir(parents=True, exist_ok=True)
            self._cached_db_path = str(data_dir / "links.db")

        return self._cached_db_path

    def get_config_dir(self) -> Path:
        """Get the configuration directory (cached)."""
        if self._cached_config_dir:
            return self._cached_config_dir

        try:
            from platformdirs import user_config_dir

            config_dir = Path(user_config_dir("linkcovery"))
        except ImportError:
            config_dir = Path.home() / ".config" / "linkcovery"

        config_dir.mkdir(parents=True, exist_ok=True)
        self._cached_config_dir = config_dir
        return config_dir


class ConfigManager:
    """Configuration manager for loading and saving settings."""

    def __init__(self) -> None:
        self._config: AppConfig = AppConfig()
        self._config_file: Path = self._config.get_config_dir() / "config.json"
        self.load()

    @property
    def config(self) -> AppConfig:
        """Get the current configuration."""
        return self._config

    def load(self) -> None:
        """Load configuration from file."""
        if not self._config_file.exists():
            self.save()  # Create default config
            return

        try:
            with open(self._config_file, encoding="utf-8") as f:
                self._config = AppConfig(**jload(f))
        except Exception as e:
            msg = f"Failed to load configuration: {e}"
            raise ConfigurationError(msg)

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w", encoding="utf-8") as f:
                dump(self._config.model_dump(), f, indent=2)
        except Exception as e:
            msg = f"Failed to save configuration: {e}"
            raise ConfigurationError(msg)

    def get(self, key: str):
        """Get a configuration value."""
        try:
            return getattr(self._config, key)
        except AttributeError:
            msg = f"Unknown configuration key: {key}"
            raise ConfigurationError(msg)

    def set(self, key: str, value) -> None:
        """Set a configuration value."""
        if not hasattr(self._config, key):
            msg = f"Unknown configuration key: {key}"
            raise ConfigurationError(msg)

        try:
            # Create a new config with the updated value
            config_dict = self._config.model_dump()
            config_dict[key] = value
            self._config = AppConfig(**config_dict)
            self.save()
        except Exception as e:
            msg = f"Failed to set configuration: {e}"
            raise ConfigurationError(msg)

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = AppConfig()
        self.save()

    def list_all(self) -> dict:
        """Get all configuration values."""
        return self._config.model_dump()


# Global configuration manager
_config_manager: ConfigManager | None = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.config


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
