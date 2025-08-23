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
        return self.update_link(link_id, url=normalize_url(str(self.get_link(link_id).url)))

    def normalize_all_links(self) -> list[Link]:
        """Normalize all links' URLs and domains."""
        normalized_links = []

        for link in self.list_all_links():
            try:
                normalized_links.append(self.normalize_link(link.id))
            except Exception:
                continue

        return normalized_links

    def get_random_links(self, number: int = 5, unread_only: bool = True) -> list[Link]:
        """Get random links, optionally filtering for unread links only."""
        return self.db.get_random_links(limit=number, unread_only=unread_only)

    def get_statistics(self) -> dict:
        """Get link statistics."""
        return self.db.get_statistics()
