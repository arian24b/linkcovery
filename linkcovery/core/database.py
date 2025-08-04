"""Modern database service for LinKCovery."""

from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import create_engine, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from linkcovery.core.config import get_config
from linkcovery.core.exceptions import DatabaseError, LinkAlreadyExistsError, LinkNotFoundError
from linkcovery.core.models import Base, Link, LinkCreate, LinkFilter, LinkUpdate


class DatabaseService:
    """Modern database service with proper error handling and context management."""

    def __init__(self, database_path: str | None = None) -> None:
        """Initialize database service."""
        if database_path is None:
            database_path = get_config().get_database_path()

        try:
            self.engine = create_engine(f"sqlite:///{database_path}")
            Base.metadata.create_all(bind=self.engine)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        except Exception as e:
            msg = f"Failed to initialize database: {e}"
            raise DatabaseError(msg)

    @contextmanager
    def get_session(self) -> Generator[Session]:
        """Get a database session with proper cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_link(self, link_data: LinkCreate) -> Link:
        """Create a new link."""
        try:
            with self.get_session() as session:
                # Check if link already exists
                existing = session.query(Link).filter(Link.url == link_data.url).first()
                if existing:
                    raise LinkAlreadyExistsError(link_data.url)

                # Create new link
                now = datetime.utcnow().isoformat()
                link = Link(
                    url=link_data.url,
                    domain=link_data.extract_domain(),
                    description=link_data.description,
                    tag=link_data.tag,
                    is_read=link_data.is_read,
                    created_at=now,
                    updated_at=now,
                )

                session.add(link)
                session.flush()  # Get the ID before committing
                session.expunge(link)  # Detach from session
                return link

        except LinkAlreadyExistsError:
            raise
        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise LinkAlreadyExistsError(link_data.url)
            msg = f"Database constraint error: {e}"
            raise DatabaseError(msg)
        except SQLAlchemyError as e:
            msg = f"Database error while creating link: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while creating link: {e}"
            raise DatabaseError(msg)

    def get_link(self, link_id: int) -> Link:
        """Get a link by ID."""
        try:
            with self.get_session() as session:
                link = session.query(Link).filter(Link.id == link_id).first()
                if not link:
                    raise LinkNotFoundError(link_id)
                session.expunge(link)  # Detach from session
                return link
        except LinkNotFoundError:
            raise
        except SQLAlchemyError as e:
            msg = f"Database error while retrieving link: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while retrieving link: {e}"
            raise DatabaseError(msg)

    def get_all_links(self) -> list[Link]:
        """Get all links ordered by creation date."""
        try:
            with self.get_session() as session:
                links = session.query(Link).order_by(Link.created_at.desc()).all()
                for link in links:
                    session.expunge(link)  # Detach from session
                return links
        except SQLAlchemyError as e:
            msg = f"Database error while retrieving links: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while retrieving links: {e}"
            raise DatabaseError(msg)

    def search_links(self, filters: LinkFilter) -> list[Link]:
        """Search links with filters."""
        try:
            with self.get_session() as session:
                query = session.query(Link)

                # Apply filters
                if filters.query:
                    query = query.filter(
                        or_(
                            Link.url.contains(filters.query),
                            Link.description.contains(filters.query),
                            Link.tag.contains(filters.query),
                        ),
                    )

                if filters.domain:
                    query = query.filter(Link.domain.contains(filters.domain))

                if filters.tag:
                    query = query.filter(Link.tag.contains(filters.tag))

                if filters.is_read is not None:
                    query = query.filter(Link.is_read == filters.is_read)

                links = query.order_by(Link.created_at.desc()).limit(filters.limit).all()
                for link in links:
                    session.expunge(link)  # Detach from session
                return links

        except SQLAlchemyError as e:
            msg = f"Database error while searching links: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while searching links: {e}"
            raise DatabaseError(msg)

    def update_link(self, link_id: int, updates: LinkUpdate) -> Link:
        """Update an existing link."""
        try:
            with self.get_session() as session:
                link = session.query(Link).filter(Link.id == link_id).first()
                if not link:
                    raise LinkNotFoundError(link_id)

                # Apply updates only for fields that were actually set
                update_data = updates.model_dump(exclude_unset=True, exclude_none=True)

                if "url" in update_data:
                    # Update domain if URL changed
                    from urllib.parse import urlparse

                    link.domain = urlparse(update_data["url"]).netloc.lower()
                    link.url = update_data["url"]

                for key, value in update_data.items():
                    if key != "url":  # URL already handled above
                        setattr(link, key, value)

                # Update timestamp
                link.updated_at = datetime.utcnow().isoformat()

                session.flush()
                session.expunge(link)  # Detach from session
                return link

        except LinkNotFoundError:
            raise
        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise LinkAlreadyExistsError(updates.url or "")
            msg = f"Database constraint error: {e}"
            raise DatabaseError(msg)
        except SQLAlchemyError as e:
            msg = f"Database error while updating link: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while updating link: {e}"
            raise DatabaseError(msg)

    def delete_link(self, link_id: int) -> None:
        """Delete a link."""
        try:
            with self.get_session() as session:
                link = session.query(Link).filter(Link.id == link_id).first()
                if not link:
                    raise LinkNotFoundError(link_id)

                session.delete(link)

        except LinkNotFoundError:
            raise
        except SQLAlchemyError as e:
            msg = f"Database error while deleting link: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while deleting link: {e}"
            raise DatabaseError(msg)

    def get_statistics(self) -> dict:
        """Get database statistics."""
        try:
            with self.get_session() as session:
                total_links = session.query(Link).count()
                read_links = session.query(Link).filter(Link.is_read == True).count()  # noqa: E712
                unread_links = total_links - read_links

                # Get top domains
                domains = {}
                for link in session.query(Link).all():
                    # Access the actual value, not the column
                    domain_value = getattr(link, "domain", "unknown")
                    domains[domain_value] = domains.get(domain_value, 0) + 1

                top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]

                return {
                    "total_links": total_links,
                    "read_links": read_links,
                    "unread_links": unread_links,
                    "top_domains": top_domains,
                }

        except SQLAlchemyError as e:
            msg = f"Database error while getting statistics: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while getting statistics: {e}"
            raise DatabaseError(msg)


# Global database service instance
_db_service: DatabaseService | None = None


def get_database() -> DatabaseService:
    """Get the global database service instance."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
