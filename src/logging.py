from logger import getLogger, Formatter, DEBUG
from rich.console import Console
from rich.logging import RichHandler


class Logger:
    def __init__(self, name: str):
        self.console = Console()
        self.logger = getLogger(name)
        self.logger.setLevel(DEBUG)
        log_handler = RichHandler(rich_tracebacks=True)
        log_handler.setLevel(DEBUG)

        formatter = Formatter("[%(asctime)s] %(name)s - %(levelname)s: %(message)s")
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
