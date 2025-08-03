"""Settings module using the new config management system."""

from rich import pretty, traceback

from app.core.config import config_manager


class Settings:
    """Settings class that uses the config manager."""

    def __init__(self) -> None:
        self.config = config_manager.config

    @property
    def APP_NAME(self) -> str:
        return self.config.app_name

    @property
    def DATABASE_NAME(self) -> str:
        return self.config.database_path

    @property
    def DEBUG(self) -> bool:
        return self.config.debug

    @property
    def ALLOW_EXTENSIONS(self) -> list[str]:
        return self.config.allowed_extensions

    @property
    def DEFAULT_EXPORT_FORMAT(self) -> str:
        return self.config.default_export_format

    @property
    def MAX_SEARCH_RESULTS(self) -> int:
        return self.config.max_search_results


settings = Settings()


if settings.DEBUG:
    traceback.install(show_locals=True)
    pretty.install()
