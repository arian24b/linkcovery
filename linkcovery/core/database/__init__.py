"""Database package with improved session management."""

from collections.abc import Generator
from contextlib import contextmanager

from linkcovery.core.database.crud import LinkService
from linkcovery.core.database.models import Link
from linkcovery.core.database.session_manager import db_manager


@contextmanager
def get_link_service() -> Generator[LinkService]:
    """Context manager that provides a link service with proper session management."""
    with db_manager.get_session() as session:
        yield LinkService(session)


def get_legacy_link_service() -> LinkService:
    """Create legacy link service for backward compatibility.

    TODO: Remove this after refactoring all CLI commands to use get_link_service().
    WARNING: This creates a service without proper session management.
    """
    # This is a simplified version for backward compatibility
    # It should be replaced with the context manager version
    session = db_manager.SessionLocal()
    return LinkService(session)


# For backward compatibility - lazy initialization
class _LazyLinkService:
    """Lazy initialization wrapper for link service."""

    def __getattr__(self, name):
        """Delegate attribute access to a fresh link service instance."""
        service = get_legacy_link_service()
        return getattr(service, name)


# Legacy service for backward compatibility
link_service = _LazyLinkService()

__all__ = ["Link", "db_manager", "get_link_service", "link_service"]
