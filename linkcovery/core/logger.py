from logging import DEBUG, INFO, Formatter, getLogger

from rich.console import Console
from rich.logging import RichHandler

from linkcovery.core.settings import config_manager


class Logger:
    def __init__(self, name: str) -> None:
        self.console = Console()
        self.logger = getLogger(name)
        debug_mode = config_manager.config.debug
        self.logger.setLevel(DEBUG if debug_mode else INFO)
        log_handler = RichHandler(
            show_time=debug_mode,
            show_level=debug_mode,
            show_path=debug_mode,
            rich_tracebacks=True,
            console=self.console,
        )
        log_handler.setLevel(DEBUG if debug_mode else INFO)

        if debug_mode:
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
