"""Configuration management system for LinKCovery CLI tool."""

import json
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir, user_data_dir
from pydantic import BaseModel


class AppConfig(BaseModel):
    """Application configuration model."""

    database_path: str = ""
    debug: bool = False
    allowed_extensions: list[str] = [".txt", ".csv", ".json"]
    default_export_format: str = "json"
    max_search_results: int = 10
    app_name: str = "LinkCovery"

    def __post_init__(self):
        """Set default database path if not provided."""
        if not self.database_path:
            data_dir = Path(user_data_dir("linkcovery"))
            data_dir.mkdir(parents=True, exist_ok=True)
            self.database_path = str(data_dir / "app.db")


class ConfigManager:
    """Manages application configuration with CLI-based updates."""

    def __init__(self) -> None:
        self.config_dir = Path(user_config_dir("linkcovery"))
        self.config_file = self.config_dir / "config.json"
        self._config: AppConfig | None = None

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    @property
    def config(self) -> AppConfig:
        """Get current configuration, loading from file if needed."""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def load_config(self) -> AppConfig:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    data = json.load(f)
                config = AppConfig(**data)
            except (json.JSONDecodeError, Exception):
                # If config is corrupted, create new default
                config = AppConfig()
                self.save_config(config)
        else:
            # Create default config
            config = AppConfig()
            # Set default database path
            data_dir = Path(user_data_dir("linkcovery"))
            data_dir.mkdir(parents=True, exist_ok=True)
            config.database_path = str(data_dir / "app.db")
            self.save_config(config)

        return config

    def save_config(self, config: AppConfig) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, indent=2)
        self._config = config

    def get_setting(self, key: str) -> Any:
        """Get a specific setting value."""
        return getattr(self.config, key, None)

    def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting value."""
        if not hasattr(self.config, key):
            return False

        # Create a new config with updated value
        config_dict = self.config.model_dump()
        config_dict[key] = value

        try:
            new_config = AppConfig(**config_dict)
            self.save_config(new_config)
            return True
        except Exception:
            return False

    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        default_config = AppConfig()
        # Set default database path
        data_dir = Path(user_data_dir("linkcovery"))
        data_dir.mkdir(parents=True, exist_ok=True)
        default_config.database_path = str(data_dir / "app.db")
        self.save_config(default_config)

    def get_config_dict(self) -> dict[str, Any]:
        """Get configuration as dictionary."""
        return self.config.model_dump()

    def get_config_file_path(self) -> str:
        """Get path to configuration file."""
        return str(self.config_file)


# Global config manager instance
config_manager = ConfigManager()
