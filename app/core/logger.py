from logging import getLogger, Formatter, DEBUG, INFO
from rich.console import Console
from rich.logging import RichHandler

from .settings import settings


class AppLogger:
    def __init__(self, name: str):
        self.console = Console()
        self.logger = getLogger(name)
        self.logger.setLevel(DEBUG if settings.DEBUG else INFO)
        log_handler = RichHandler(
            show_time=settings.DEBUG,
            show_level=settings.DEBUG,
            show_path=settings.DEBUG,
            rich_tracebacks=True,
            console=self.console,
        )
        log_handler.setLevel(DEBUG if settings.DEBUG else INFO)

        if settings.DEBUG:
            formatter = Formatter("[%(asctime)s] %(name)s - %(levelname)s: %(message)s")
        else:
            formatter = Formatter("%(message)s")
        log_handler.setFormatter(formatter)

        self.logger.addHandler(log_handler)

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)

    def critical(self, msg: str) -> None:
        self.logger.critical(msg)

    def exception(self, msg: str) -> None:
        self.logger.exception(msg)

    def print(self, msg: str) -> None:
        self.console.print(msg)
