"""Link management service for handling business logic."""

from linkcovery.core.database import DatabaseService, get_database
from linkcovery.core.models import Link, LinkCreate, LinkFilter, LinkUpdate
from linkcovery.core.utils import normalize_url


class LinkService:
    """Service for link management operations."""

    def __init__(self, db: DatabaseService | None = None) -> None:
        """Initialize link service with database dependency."""
        self.db = db or get_database()

    def add_link(self, url: str, description: str = "", tag: str = "", is_read: bool = False) -> Link:
        """Add a new link with validation."""
        link_data = LinkCreate(
            url=url,
            description=description,
            tag=tag,
            is_read=is_read,
        )
        return self.db.create_link(link_data)

    def get_link(self, link_id: int) -> Link:
        """Get a link by ID."""
        return self.db.get_link(link_id)

    def list_all_links(self) -> list[Link]:
        """Get all links."""
        return self.db.get_all_links()

    def search_links(
        self,
        query: str = "",
        domain: str = "",
        tag: str = "",
        is_read: bool | None = None,
        limit: int = 50,
    ) -> list[Link]:
        """Search links with filters."""
        filters = LinkFilter(
            query=query,
            domain=domain,
            tag=tag,
            is_read=is_read,
            limit=limit,
        )
        return self.db.search_links(filters)

    def update_link(
        self,
        link_id: int,
        url: str | None = None,
        description: str | None = None,
        tag: str | None = None,
        is_read: bool | None = None,
    ) -> Link:
        """Update an existing link."""
        updates = LinkUpdate(
            url=url,
            description=description,
            tag=tag,
            is_read=is_read,
        )
        return self.db.update_link(link_id, updates)

    def delete_link(self, link_id: int) -> None:
        """Delete a link."""
        self.db.delete_link(link_id)

    def mark_as_read(self, link_id: int) -> Link:
        """Mark a link as read."""
        return self.update_link(link_id, is_read=True)

    def mark_as_unread(self, link_id: int) -> Link:
        """Mark a link as unread."""
        return self.update_link(link_id, is_read=False)

    def normalize_link(self, link_id: int) -> Link:
        """Normalize a link's URL and domain."""
        # Get the current link
        current_link = self.get_link(link_id)

        # Normalize the URL
        normalized_url = normalize_url(current_link.url)

        # Update the link with normalized URL (domain will be auto-updated)
        return self.update_link(link_id, url=normalized_url)

    def normalize_all_links(self) -> list[Link]:
        """Normalize all links' URLs and domains."""
        all_links = self.list_all_links()
        normalized_links = []

        for link in all_links:
            try:
                normalized_link = self.normalize_link(link.id)
                normalized_links.append(normalized_link)
            except Exception:
                # Skip links that fail to normalize and continue with the rest
                continue

        return normalized_links

    def get_statistics(self) -> dict:
        """Get link statistics."""
        return self.db.get_statistics()


# Global service instance
_link_service: LinkService | None = None


def get_link_service() -> LinkService:
    """Get the global link service instance."""
    global _link_service
    if _link_service is None:
        _link_service = LinkService()
    return _link_service
