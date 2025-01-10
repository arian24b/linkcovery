from sqlite3 import IntegrityError
from json import dumps, loads
from typing import List, Optional
from datetime import datetime
from rich import print

from .database import Database
from .schema import User, Link


class LinkDatabase(Database):
    def create_table(self):
        """Create users and links tables."""
        # Create the users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)

        # Create the links table with a foreign key to users
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                domain TEXT NOT NULL,
                description TEXT,
                tag TEXT,
                author_id INTEGER NOT NULL,
                is_read INTEGER DEFAULT 0, -- New column added
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
        """)
        self.connection.commit()

    def create_user(self, user: User):
        """Insert a new user."""
        try:
            self.cursor.execute(
                """
                INSERT INTO users (name, email)
                VALUES (?, ?)
            """,
                (user.name, user.email),
            )
            self.connection.commit()
            print("User created successfully.")
        except IntegrityError:
            print(f"User with email {user.email} already exists. Skipping insertion.")

    def create_link(self, link: Link):
        """Insert a new link."""
        try:
            self.cursor.execute(
                """
                INSERT INTO links (url, domain, description, tag, author_id, is_read, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    str(link.url),
                    link.domain,
                    link.description,
                    dumps(link.tag),
                    link.author_id,
                    int(link.is_read),
                    link.created_at,
                    link.updated_at,
                ),
            )
            self.connection.commit()
            print("Link created successfully.")
        except IntegrityError:
            print(f"User with email {str(link.url)} already exists. Skipping insertion.")

    def read_users(self) -> List[User]:
        """Retrieve all users."""
        self.cursor.execute("SELECT * FROM users")
        rows = self.cursor.fetchall()
        return [User(**dict(row)) for row in rows]

    def read_links_with_authors(self) -> List[dict]:
        """Retrieve all links with their authors."""
        self.cursor.execute("""
            SELECT links.*, users.name as author_name, users.email as author_email
            FROM links
            JOIN users ON links.author_id = users.id
        """)
        rows = self.cursor.fetchall()

        results = []
        for row in rows:
            row_dict = dict(row)
            # Extract link fields explicitly
            link_data = {key: row_dict[key] for key in Link.__fields__.keys()}
            link_data["tag"] = loads(link_data["tag"])  # Convert JSON string to list
            link = Link(**link_data)

            # Extract author information
            author = {
                "name": row_dict["author_name"],
                "email": row_dict["author_email"],
            }

            results.append({"link": link, "author": author})

        return results

    def read_link(self, link_id: int) -> Optional[Link]:
        """Retrieve a specific link by ID."""
        self.cursor.execute("SELECT * FROM links WHERE id = ?", (link_id,))
        row = self.cursor.fetchone()
        if row:
            return Link(**dict(row), tag=loads(row["tag"]))
        return None

    def update_link(self, link_id: int, updated_link: Link):
        """Update a link by ID."""
        updated_link.updated_at = datetime.utcnow().isoformat()
        self.cursor.execute(
            """
            UPDATE links
            SET url = ?, domain = ?, description = ?, tag = ?, updated_at = ?
            WHERE id = ?
        """,
            (
                updated_link.url,
                updated_link.domain,
                updated_link.description,
                dumps(updated_link.tag),
                updated_link.updated_at,
                link_id,
            ),
        )
        self.connection.commit()
        print("Link updated successfully.")

    def delete_link(self, link_id: int):
        """Delete a link by ID."""
        self.cursor.execute("DELETE FROM links WHERE id = ?", (link_id,))
        self.connection.commit()
        print("Link deleted successfully.")

    def search_links(
        self,
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "ASC",
        limit: int = 10,
        offset: int = 0,
    ) -> List[Link]:
        """Search for links by domain, tags, or description with sorting and pagination."""
        query = "SELECT * FROM links WHERE 1=1"
        parameters = []

        # Filter by domain (case-insensitive)
        if domain:
            query += " AND LOWER(domain) LIKE ?"
            parameters.append(f"%{domain.lower()}%")

        # Filter by description (case-insensitive)
        if description:
            query += " AND LOWER(description) LIKE ?"
            parameters.append(f"%{description.lower()}%")

        # Filter by tags (exact match, tag list must contain all tags)
        if tags:
            self.cursor.execute("SELECT * FROM links")
            rows = self.cursor.fetchall()
            filtered_links = []
            for row in rows:
                row_dict = dict(row)
                row_tags = loads(row_dict["tag"])  # Deserialize tags
                if all(tag in row_tags for tag in tags):
                    filtered_links.append(row_dict)
            # Return results after tag filtering
            rows = filtered_links
        else:
            # Sort by field (case-insensitive for text fields)
            if sort_by not in {"created_at", "updated_at", "domain"}:
                raise ValueError("Invalid sort_by field")
            query += f" ORDER BY {sort_by} {sort_order.upper()}"
            if sort_order.upper() not in {"ASC", "DESC"}:
                raise ValueError("Invalid sort_order; use 'ASC' or 'DESC'")

            # Add pagination
            query += " LIMIT ? OFFSET ?"
            parameters.extend([limit, offset])

            # Execute the query
            self.cursor.execute(query, parameters)
            rows = self.cursor.fetchall()

        # Convert rows to Link objects
        links = []
        for row in rows:
            row_dict = dict(row)
            row_dict["tag"] = loads(row_dict["tag"])  # Convert JSON string to list
            links.append(Link(**row_dict))

        return links
