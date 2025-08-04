"""Simple and clean database operations for LinKCovery."""

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from linkcovery.core.models import Base, Link


class LinkDatabase:
    """Simple database service for link management."""

    def __init__(self, database_path: str | None = None) -> None:
        if database_path is None:
            # Use platformdirs for cross-platform data directory
            try:
                from platformdirs import user_data_dir

                data_dir = Path(user_data_dir("linkcovery"))
                data_dir.mkdir(parents=True, exist_ok=True)
                database_path = str(data_dir / "links.db")
            except ImportError:
                # Fallback if platformdirs not available
                database_path = str(Path.home() / ".linkcovery" / "links.db")
                Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = SessionLocal()

    def _validate_url(self, url: str) -> str:
        """Validate URL format."""
        if not url or not isinstance(url, str):
            msg = "URL is required and must be a string"
            raise ValueError(msg)

        url = url.strip()
        if not url.startswith(("http://", "https://")):
            msg = "URL must start with http:// or https://"
            raise ValueError(msg)

        return url

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if not domain:
                msg = "Could not extract domain from URL"
                raise ValueError(msg)
            return domain
        except Exception as e:
            msg = f"Invalid URL format: {e}"
            raise ValueError(msg)

    def add_link(self, url: str, description: str = "", tag: str = "", is_read: bool = False) -> Link:
        """Add a new link to the database."""
        try:
            # Validate and clean URL
            url = self._validate_url(url)
            domain = self._extract_domain(url)

            # Check if link already exists
            existing = self.session.query(Link).filter(Link.url == url).first()
            if existing:
                msg = f"Link already exists: {url}"
                raise ValueError(msg)

            # Create timestamps
            now = datetime.utcnow().isoformat()

            # Create and save link
            link = Link(
                url=url,
                domain=domain,
                description=description.strip(),
                tag=tag.strip(),
                is_read=is_read,
                created_at=now,
                updated_at=now,
            )

            self.session.add(link)
            self.session.commit()
            return link

        except Exception:
            self.session.rollback()
            raise

    def get_link(self, link_id: int) -> Link | None:
        """Get a link by ID."""
        return self.session.query(Link).filter(Link.id == link_id).first()

    def get_all_links(self) -> list[Link]:
        """Get all links."""
        return self.session.query(Link).order_by(Link.created_at.desc()).all()

    def search_links(
        self,
        query: str = "",
        domain: str = "",
        tag: str = "",
        is_read: bool | None = None,
        limit: int = 50,
    ) -> list[Link]:
        """Search links with filters."""
        q = self.session.query(Link)

        if query:
            q = q.filter((Link.url.contains(query)) | (Link.description.contains(query)) | (Link.tag.contains(query)))

        if domain:
            q = q.filter(Link.domain.contains(domain))

        if tag:
            q = q.filter(Link.tag.contains(tag))

        if is_read is not None:
            q = q.filter(Link.is_read == is_read)

        return q.order_by(Link.created_at.desc()).limit(limit).all()

    def update_link(self, link_id: int, **updates) -> bool:
        """Update a link."""
        link = self.get_link(link_id)
        if not link:
            msg = f"Link with ID {link_id} not found"
            raise ValueError(msg)

        # Validate URL if being updated
        if "url" in updates:
            updates["url"] = self._validate_url(updates["url"])
            updates["domain"] = self._extract_domain(updates["url"])

        # Update fields
        for key, value in updates.items():
            if hasattr(link, key):
                setattr(link, key, value)

        # Update timestamp
        link.updated_at = datetime.utcnow().isoformat()

        try:
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            raise

    def delete_link(self, link_id: int) -> bool:
        """Delete a link."""
        link = self.get_link(link_id)
        if not link:
            msg = f"Link with ID {link_id} not found"
            raise ValueError(msg)

        try:
            self.session.delete(link)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            raise

    def close(self) -> None:
        """Close the database session."""
        self.session.close()


# Global database instance
_db = None


def get_database() -> LinkDatabase:
    """Get the global database instance."""
    global _db
    if _db is None:
        _db = LinkDatabase()
    return _db
