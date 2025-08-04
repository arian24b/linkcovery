"""Custom exceptions for LinKCovery."""


class LinKCoveryError(Exception):
    """Base exception for all LinKCovery errors."""

    def __init__(self, message: str, details: str = "") -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)


class DatabaseError(LinKCoveryError):
    """Raised when database operations fail."""


class ValidationError(LinKCoveryError):
    """Raised when data validation fails."""


class LinkNotFoundError(LinKCoveryError):
    """Raised when a requested link is not found."""

    def __init__(self, link_id: int) -> None:
        super().__init__(f"Link with ID {link_id} not found")
        self.link_id = link_id


class LinkAlreadyExistsError(LinKCoveryError):
    """Raised when trying to add a link that already exists."""

    def __init__(self, url: str) -> None:
        super().__init__(f"Link already exists: {url}")
        self.url = url


class ConfigurationError(LinKCoveryError):
    """Raised when configuration issues occur."""


class ImportExportError(LinKCoveryError):
    """Raised when import/export operations fail."""
