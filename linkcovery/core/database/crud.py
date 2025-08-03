from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from linkcovery.core.database.models import Link
from linkcovery.core.database.repositories import LinkRepository
from linkcovery.core.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ServiceError,
    handle_service_errors,
)


class LinkService:
    """Enhanced link service with proper error handling."""

    def __init__(self, session: Session) -> None:
        self.link_repository = LinkRepository(session)

    @handle_service_errors("create link")
    def create_link(self, **link_data: Any) -> Link | None:
        """Create a new link with enhanced error handling."""
        try:
            link_data["created_at"] = datetime.utcnow().isoformat()
            link_data["updated_at"] = link_data["created_at"]
            return self.link_repository.create(link_data)
        except ValueError as e:
            if "already exists" in str(e):
                msg = "Link"
                raise EntityAlreadyExistsError(msg, link_data.get("url", "unknown")) from e
            msg = f"Failed to create link: {e}"
            raise ServiceError(msg) from e

    @handle_service_errors("get link")
    def get_link(self, link_id: int | None = None, link_url: str | None = None) -> Link | None:
        """Get a link by ID or URL."""
        if link_id:
            return self.link_repository.get_by_id(link_id)
        if link_url:
            return self.link_repository.get_by_url(link_url)
        return None

    @handle_service_errors("search links")
    def search_links(self, search_criteria: dict[str, Any]) -> list[Link]:
        """Search links based on criteria."""
        return self.link_repository.search(search_criteria)

    @handle_service_errors("update link")
    def update_link(self, link_id: int, **link_data: Any) -> bool:
        """Update a link."""
        link_data["updated_at"] = datetime.utcnow().isoformat()
        updated_link = self.link_repository.update(link_id, link_data)
        if not updated_link:
            msg = "Link"
            raise EntityNotFoundError(msg, link_id)
        return True

    @handle_service_errors("delete link")
    def delete_link(self, link_id: int) -> None:
        """Delete a link."""
        # Check if link exists first
        if not self.link_repository.get_by_id(link_id):
            msg = "Link"
            raise EntityNotFoundError(msg, link_id)
        self.link_repository.delete(link_id)

    @handle_service_errors("get links")
    def get_links(self) -> list[Link]:
        """Get all links."""
        return self.link_repository.get_all()
