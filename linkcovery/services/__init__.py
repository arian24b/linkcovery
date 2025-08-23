"""Service layer for LinKCovery - separating business logic from CLI."""

from linkcovery.services.data_service import DataService
from linkcovery.services.link_service import LinkService

# Global service instance
_data_service: DataService | None = None
_link_service: LinkService | None = None


def get_data_service() -> DataService:
    """Get the global import/export service instance."""
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service


def get_link_service() -> LinkService:
    """Get the global link service instance."""
    global _link_service
    if _link_service is None:
        _link_service = LinkService()
    return _link_service
