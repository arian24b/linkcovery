"""Custom exception hierarchy for LinKCovery."""

from typing import Any


class LinKCoveryError(Exception):
    """Base exception for all LinKCovery errors."""

    def __init__(self, message: str, error_code: str | None = None, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}


class DatabaseError(LinKCoveryError):
    """Base class for database-related errors."""


class EntityNotFoundError(DatabaseError):
    """Raised when an entity is not found in the database."""

    def __init__(self, entity_type: str, identifier: str | int, details: dict[str, Any] | None = None) -> None:
        message = f"{entity_type} with identifier '{identifier}' not found"
        super().__init__(message, "ENTITY_NOT_FOUND", details)
        self.entity_type = entity_type
        self.identifier = identifier


class EntityAlreadyExistsError(DatabaseError):
    """Raised when trying to create an entity that already exists."""

    def __init__(self, entity_type: str, identifier: str | int, details: dict[str, Any] | None = None) -> None:
        message = f"{entity_type} with identifier '{identifier}' already exists"
        super().__init__(message, "ENTITY_ALREADY_EXISTS", details)
        self.entity_type = entity_type
        self.identifier = identifier


class ServiceError(LinKCoveryError):
    """Raised when a service operation fails."""


class RepositoryError(DatabaseError):
    """Raised when a repository operation fails."""


class ImportExportError(LinKCoveryError):
    """Raised when import/export operations fail."""


# Error handler decorator
def handle_service_errors(operation_name: str):
    """Decorator to handle service errors consistently."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except LinKCoveryError:
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Convert generic exceptions to ServiceError
                msg = f"Failed to {operation_name}: {e!s}"
                raise ServiceError(msg) from e

        return wrapper

    return decorator
