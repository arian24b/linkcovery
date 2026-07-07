"""Database service for LinkCovery using sqlite3."""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from linkcovery.core.config import get_config
from linkcovery.core.exceptions import DatabaseError, LinkAlreadyExistsError, LinkNotFoundError
from linkcovery.core.models import Link, LinkCreate, LinkFilter, LinkUpdate
from linkcovery.core.utils import extract_domain


def _row_to_link(row: tuple) -> Link:
    """Convert a database row to a Link object."""
    return Link(
        id=row[0],
        url=row[1],
        domain=row[2],
        description=row[3] or "",
        tag=row[4] or "",
        is_read=bool(row[5]),
        preview_url=row[6] or "",
        created_at=row[7],
        updated_at=row[8],
    )


class DatabaseService:
    """Database service using sqlite3."""

    def __init__(self, database_path: str | None = None) -> None:
        """Initialize database service."""
        if database_path is None:
            database_path = get_config().get_database_path()

        self.database_path = database_path
        self._connection: sqlite3.Connection | None = None
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.database_path,
                timeout=20,
                check_same_thread=False,
            )
            self._connection.row_factory = sqlite3.Row
            self._apply_pragmas()
        return self._connection

    def _apply_pragmas(self) -> None:
        """Apply SQLite optimization pragmas."""
        conn = self._connection
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")
        cursor.close()

    def _init_database(self) -> None:
        """Initialize the database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                domain TEXT NOT NULL,
                description TEXT DEFAULT '',
                tag TEXT DEFAULT '',
                is_read INTEGER DEFAULT 0,
                preview_url TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_domain ON links(domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_tag ON links(tag)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_is_read ON links(is_read)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_created_at ON links(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain_is_read ON links(domain, is_read)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag_is_read ON links(tag, is_read)")
        conn.commit()

    @contextmanager
    def get_session(self) -> Generator[None]:
        """Get a database session context."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def exists(self, link_url: str) -> bool:
        """Check if a link with the given URL exists."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM links WHERE url = ?", (link_url,))
            return cursor.fetchone() is not None
        except Exception as e:
            msg = f"Database error while checking link existence: {e}"
            raise DatabaseError(msg)

    def create_link(self, link_data: LinkCreate) -> Link:
        """Create a new link."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if link already exists
            cursor.execute("SELECT id FROM links WHERE url = ?", (link_data.url,))
            if cursor.fetchone():
                raise LinkAlreadyExistsError(link_data.url)

            # Create new link
            now = datetime.now(UTC).isoformat()
            domain = extract_domain(url=link_data.url)

            cursor.execute(
                """INSERT INTO links (url, domain, description, tag, is_read, preview_url, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    link_data.url,
                    domain,
                    link_data.description or "",
                    link_data.tag or "",
                    1 if link_data.is_read else 0,
                    "",
                    now,
                    now,
                ),
            )
            link_id = cursor.lastrowid
            conn.commit()

            return Link(
                id=link_id,
                url=link_data.url,
                domain=domain,
                description=link_data.description or "",
                tag=link_data.tag or "",
                is_read=link_data.is_read,
                preview_url="",
                created_at=now,
                updated_at=now,
            )

        except LinkAlreadyExistsError:
            raise
        except Exception as e:
            msg = f"Database error while creating link: {e}"
            raise DatabaseError(msg)

    def get_link(self, link_id: int) -> Link:
        """Get a link by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM links WHERE id = ?", (link_id,))
            row = cursor.fetchone()
            if not row:
                raise LinkNotFoundError(link_id)
            return _row_to_link(row)
        except LinkNotFoundError:
            raise
        except Exception as e:
            msg = f"Database error while retrieving link: {e}"
            raise DatabaseError(msg)

    def get_all_links(self) -> list[Link]:
        """Get all links ordered by creation date."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM links ORDER BY created_at DESC")
            return [_row_to_link(row) for row in cursor.fetchall()]
        except Exception as e:
            msg = f"Database error while retrieving links: {e}"
            raise DatabaseError(msg)

    def get_links_paginated(self, offset: int = 0, limit: int = 50) -> list[Link]:
        """Get links with pagination."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM links ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
            return [_row_to_link(row) for row in cursor.fetchall()]
        except Exception as e:
            msg = f"Database error while retrieving links: {e}"
            raise DatabaseError(msg)

    def search_links(self, filters: LinkFilter) -> list[Link]:
        """Search links with filters."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "SELECT * FROM links WHERE 1=1"
            params: list[Any] = []

            if filters.query:
                query += " AND (url LIKE ? OR description LIKE ? OR tag LIKE ?)"
                search_term = f"%{filters.query}%"
                params.extend([search_term, search_term, search_term])

            if filters.domain:
                query += " AND domain LIKE ?"
                params.append(f"%{filters.domain}%")

            if filters.tag:
                query += " AND tag LIKE ?"
                params.append(f"%{filters.tag}%")

            if filters.is_read is not None:
                query += " AND is_read = ?"
                params.append(1 if filters.is_read else 0)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(filters.limit)

            cursor.execute(query, params)
            return [_row_to_link(row) for row in cursor.fetchall()]
        except Exception as e:
            msg = f"Database error while searching links: {e}"
            raise DatabaseError(msg)

    def search_links_paginated(self, filters: LinkFilter) -> list[Link]:
        """Search links with filters and pagination support."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "SELECT * FROM links WHERE 1=1"
            count_query = "SELECT COUNT(*) FROM links WHERE 1=1"
            params: list[Any] = []

            if filters.query:
                clause = " AND (url LIKE ? OR description LIKE ? OR tag LIKE ?)"
                search_term = f"%{filters.query}%"
                query += clause
                count_query += clause
                params.extend([search_term, search_term, search_term])

            if filters.domain:
                clause = " AND domain LIKE ?"
                query += clause
                count_query += clause
                params.append(f"%{filters.domain}%")

            if filters.tag:
                clause = " AND tag LIKE ?"
                query += clause
                count_query += clause
                params.append(f"%{filters.tag}%")

            if filters.is_read is not None:
                clause = " AND is_read = ?"
                query += clause
                count_query += clause
                params.append(1 if filters.is_read else 0)

            # Sort order
            sort_map = {
                "newest": "created_at DESC",
                "oldest": "created_at ASC",
                "domain": "domain ASC, created_at DESC",
                "read_status": "is_read ASC, created_at DESC",
            }
            query += f" ORDER BY {sort_map.get(filters.sort, 'created_at DESC')}"

            query += " LIMIT ? OFFSET ?"
            params.extend([filters.limit, filters.offset])

            cursor.execute(query, params)
            rows = [_row_to_link(row) for row in cursor.fetchall()]

            # Get total count for pagination
            cursor.execute(count_query, params[:len(params) - 2])
            total = cursor.fetchone()[0]

            # Attach total via an attribute
            rows_with_total: Any = rows
            rows_with_total._total = total
            return rows_with_total
        except Exception as e:
            msg = f"Database error while searching links: {e}"
            raise DatabaseError(msg)

    def update_link(self, link_id: int, updates: LinkUpdate) -> Link:
        """Update an existing link."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get existing link
            cursor.execute("SELECT * FROM links WHERE id = ?", (link_id,))
            row = cursor.fetchone()
            if not row:
                raise LinkNotFoundError(link_id)

            # Build update query
            update_data = updates.model_dump(exclude_unset=True, exclude_none=True)
            if not update_data:
                return _row_to_link(row)

            # Handle URL change - update domain
            if "url" in update_data:
                update_data["domain"] = extract_domain(url=update_data["url"])

            # Add updated_at timestamp
            update_data["updated_at"] = datetime.now(UTC).isoformat()

            # Handle is_read conversion
            if "is_read" in update_data:
                update_data["is_read"] = 1 if update_data["is_read"] else 0

            # Build SET clause
            set_clause = ", ".join([f"{key} = ?" for key in update_data])
            query = f"UPDATE links SET {set_clause} WHERE id = ?"
            params = [*list(update_data.values()), link_id]

            cursor.execute(query, params)
            conn.commit()

            # Return updated link
            cursor.execute("SELECT * FROM links WHERE id = ?", (link_id,))
            return _row_to_link(cursor.fetchone())

        except LinkNotFoundError:
            raise
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise LinkAlreadyExistsError(updates.url or "")
            msg = f"Database error while updating link: {e}"
            raise DatabaseError(msg)

    def delete_link(self, link_id: int) -> None:
        """Delete a link."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM links WHERE id = ?", (link_id,))
            if not cursor.fetchone():
                raise LinkNotFoundError(link_id)

            cursor.execute("DELETE FROM links WHERE id = ?", (link_id,))
            conn.commit()

        except LinkNotFoundError:
            raise
        except Exception as e:
            msg = f"Database error while deleting link: {e}"
            raise DatabaseError(msg)

    def get_random_links(self, limit: int = 5, unread_only: bool = True) -> list[Link]:
        """Get random links from the database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "SELECT * FROM links"
            if unread_only:
                query += " WHERE is_read = 0"
            query += " ORDER BY RANDOM() LIMIT ?"

            cursor.execute(query, (limit,))
            return [_row_to_link(row) for row in cursor.fetchall()]
        except Exception as e:
            msg = f"Database error while getting random links: {e}"
            raise DatabaseError(msg)

    def get_all_tags(self) -> list[dict]:
        """Get all tags with link counts."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tag, COUNT(*) as count
                FROM links
                WHERE tag != ''
                GROUP BY tag
                ORDER BY count DESC, tag ASC
            """)
            return [{"tag": row[0], "count": row[1]} for row in cursor.fetchall()]
        except Exception as e:
            msg = f"Database error while retrieving tags: {e}"
            raise DatabaseError(msg)

    def get_statistics(self) -> dict:
        """Get database statistics."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get counts
            cursor.execute("SELECT COUNT(*) FROM links")
            total_links = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM links WHERE is_read = 1")
            read_links = cursor.fetchone()[0]

            # Get top domains
            cursor.execute("""
                SELECT domain, COUNT(*) as count
                FROM links
                GROUP BY domain
                ORDER BY count DESC
                LIMIT 5
            """)
            top_domains = [(row[0], row[1]) for row in cursor.fetchall()]

            return {
                "total_links": total_links,
                "read_links": read_links,
                "unread_links": total_links - read_links,
                "top_domains": top_domains,
            }
        except Exception as e:
            msg = f"Database error while getting statistics: {e}"
            raise DatabaseError(msg)


# Global database service instance
_db_service: DatabaseService | None = None


def get_database() -> DatabaseService:
    """Get the global database service instance."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
