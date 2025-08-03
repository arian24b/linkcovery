"""Base command handler for CLI operations."""

from abc import ABC, abstractmethod
from typing import Any

from app.core.exceptions import LinKCoveryError
from app.core.logger import AppLogger


class CommandResult:
    """Represents the result of a command execution."""

    def __init__(self, success: bool, message: str, data: Any = None) -> None:
        self.success = success
        self.message = message
        self.data = data


class BaseCommandHandler(ABC):
    """Base class for command handlers."""

    def __init__(self, link_service) -> None:
        self.link_service = link_service
        self.logger = AppLogger(self.__class__.__name__)

    @abstractmethod
    def handle(self, *args, **kwargs) -> CommandResult:
        """Handle the command execution."""

    def _handle_error(self, error: Exception, operation: str) -> CommandResult:
        """Standardized error handling."""
        if isinstance(error, LinKCoveryError):
            error_msg = error.message
            self.logger.error(error_msg)
        else:
            error_msg = f"Failed to {operation}: {error!s}"
            self.logger.exception(error_msg)

        return CommandResult(success=False, message=error_msg)

    def _validate_required_params(self, **params) -> CommandResult | None:
        """Validate required parameters."""
        for key, value in params.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                return CommandResult(success=False, message=f"Parameter '{key}' is required")
        return None
