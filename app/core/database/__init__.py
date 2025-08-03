"""Database package with improved session management."""

from app.core.database.crud import LinkService
from app.core.database.models import Link
from app.core.database.session_manager import db_manager


def get_link_service() -> LinkService:
    """Factory function to create link service with proper session management."""
    with db_manager.get_session() as session:
        return LinkService(session)


# For backward compatibility - these will be deprecated
def _create_legacy_services():
    """Create legacy services for backward compatibility."""
    with db_manager.get_session() as session:
        return LinkService(session)


# Legacy services for backward compatibility
# TODO: Remove these after refactoring all CLI commands
try:
    link_service = _create_legacy_services()
except Exception:
    # Fallback if database is not available
    link_service = None

__all__ = ["Link", "db_manager", "get_link_service", "link_service"]
