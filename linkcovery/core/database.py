"""Database service for LinKCovery."""

from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy import create_engine, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from linkcovery.core.config import get_config
from linkcovery.core.exceptions import DatabaseError, LinkAlreadyExistsError, LinkNotFoundError
from linkcovery.core.models import Base, Link, LinkCreate, LinkFilter, LinkUpdate
from linkcovery.core.utils import extract_domain


class DatabaseService:
    """Database service with connection pooling and optimization."""

    def __init__(self, database_path: str | None = None) -> None:
        """Initialize database service with connection pooling."""
        if database_path is None:
            database_path = get_config().get_database_path()

        try:
            # Enable connection pooling and optimization for SQLite
            self.engine = create_engine(
                f"sqlite:///{database_path}",
                poolclass=StaticPool,
                pool_pre_ping=True,
                connect_args={
                    "check_same_thread": False,
                    # SQLite optimization pragmas
                    "timeout": 20,
                },
                echo=False,  # Disable SQL logging for performance
            )

            # Apply SQLite optimization pragmas
            with self.engine.connect() as conn:
                # Performance optimizations
                conn.exec_driver_sql("PRAGMA journal_mode=WAL")
                conn.exec_driver_sql("PRAGMA synchronous=NORMAL")
                conn.exec_driver_sql("PRAGMA cache_size=10000")
                conn.exec_driver_sql("PRAGMA temp_store=MEMORY")
                conn.exec_driver_sql("PRAGMA mmap_size=268435456")  # 256MB
                conn.commit()

            Base.metadata.create_all(bind=self.engine)
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False,  # Keep objects accessible after commit
            )
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
                if session.query(Link).filter(Link.url == link_data.url).first():
                    raise LinkAlreadyExistsError(link_data.url)

                # Create new link
                now = datetime.now(UTC).isoformat()
                link = Link(
                    url=link_data.url,
                    domain=extract_domain(url=link_data.url),
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
                if not (link := session.query(Link).filter(Link.id == link_id).first()):
                    raise LinkNotFoundError(link_id)
                session.expunge(link)  # Detach from session
                return link
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
                for link in (links := session.query(Link).order_by(Link.created_at.desc()).all()):
                    session.expunge(link)  # Detach from session
                return links
        except SQLAlchemyError as e:
            msg = f"Database error while retrieving links: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while retrieving links: {e}"
            raise DatabaseError(msg)

    def search_links(self, filters: LinkFilter) -> list[Link]:
        """Search links with filters using optimized queries."""
        try:
            with self.get_session() as session:
                query = session.query(Link)

                # Apply filters with optimized query patterns
                conditions = []

                if filters.query:
                    # Use LIKE for text search, could be optimized with FTS if needed
                    conditions.append(
                        or_(
                            Link.url.contains(filters.query),
                            Link.description.contains(filters.query),
                            Link.tag.contains(filters.query),
                        ),
                    )

                if filters.domain:
                    # Use indexed domain column
                    conditions.append(Link.domain.contains(filters.domain))

                if filters.tag:
                    # Use indexed tag column
                    conditions.append(Link.tag.contains(filters.tag))

                if filters.is_read is not None:
                    # Use indexed is_read column
                    conditions.append(Link.is_read == filters.is_read)

                # Apply all conditions at once
                if conditions:
                    from sqlalchemy import and_

                    query = query.filter(and_(*conditions))

                # Order by indexed created_at column and limit
                for link in (links := query.order_by(Link.created_at.desc()).limit(filters.limit).all()):
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
                if not (link := session.query(Link).filter(Link.id == link_id).first()):
                    raise LinkNotFoundError(link_id)

                # Apply updates only for fields that were actually set
                if "url" in (update_data := updates.model_dump(exclude_unset=True, exclude_none=True)):
                    # Update domain if URL changed
                    link.domain = extract_domain(url=update_data["url"])
                    link.url = update_data["url"]

                for key, value in update_data.items():
                    if key != "url":  # URL already handled above
                        setattr(link, key, value)

                # Update timestamp
                link.updated_at = datetime.now(UTC).isoformat()

                session.flush()
                session.expunge(link)  # Detach from session
                return link

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
                if not (link := session.query(Link).filter(Link.id == link_id).first()):
                    raise LinkNotFoundError(link_id)

                session.delete(link)

        except SQLAlchemyError as e:
            msg = f"Database error while deleting link: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while deleting link: {e}"
            raise DatabaseError(msg)

    def get_random_links(self, limit: int = 5, unread_only: bool = True) -> list[Link]:
        """Get random links from the database."""
        try:
            with self.get_session() as session:
                from sqlalchemy import func

                query = session.query(Link)

                # Filter for unread links by default
                if unread_only:
                    query = query.filter(Link.is_read == False)  # noqa: E712

                # Order randomly and limit
                for link in (links := query.order_by(func.random()).limit(limit).all()):
                    session.expunge(link)  # Detach from session
                return links

        except SQLAlchemyError as e:
            msg = f"Database error while getting random links: {e}"
            raise DatabaseError(msg)
        except Exception as e:
            msg = f"Unexpected error while getting random links: {e}"
            raise DatabaseError(msg)

    def get_statistics(self) -> dict:
        """Get database statistics with optimized queries."""
        try:
            with self.get_session() as session:
                # Get counts efficiently with single query
                total_links = session.query(Link).count()
                read_links = session.query(Link).filter(Link.is_read == True).count()  # noqa: E712

                # Get top domains efficiently with group by
                from sqlalchemy import func

                domain_counts = (
                    session.query(Link.domain, func.count(Link.domain).label("count"))
                    .group_by(Link.domain)
                    .order_by(func.count(Link.domain).desc())
                    .all()
                )

                return {
                    "total_links": total_links,
                    "read_links": read_links,
                    "unread_links": total_links - read_links,
                    "top_domains": [(domain, count) for domain, count in domain_counts],
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
