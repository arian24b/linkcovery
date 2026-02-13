"""Custom exceptions for LinKCovery."""


class LinKCoveryError(Exception):
    """Base exception for all LinkCovery errors."""

    def __init__(self, message: str, details: str = "", hint: str = "") -> None:
        self.message = message
        self.details = details
        self.hint = hint
        super().__init__(self.message)


class DatabaseError(LinKCoveryError):
    """Raised when database operations fail."""


class ValidationError(LinKCoveryError):
    """Raised when data validation fails."""


class LinkNotFoundError(LinKCoveryError):
    """Raised when a requested link is not found."""

    def __init__(self, link_id: int) -> None:
        super().__init__(f"Link with ID {link_id} not found", hint="Use 'linkCOVERY list' to see all available links")
        self.link_id = link_id


class LinkAlreadyExistsError(LinKCoveryError):
    """Raised when trying to add a link that already exists."""

    def __init__(self, url: str) -> None:
        super().__init__(f"Link already exists: {url}", hint="Use 'linkCOVERY edit <id>' to update existing link")
        self.url = url


class ConfigurationError(LinKCoveryError):
    """Raised when configuration issues occur."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message, hint=hint or "Use 'linkCOVERY config show' to see current configuration")


class ImportExportError(LinKCoveryError):
    """Raised when import/export operations fail."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message, hint=hint or "Check file permissions and format")
