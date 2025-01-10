from json import dumps, loads
from typing import List, Optional
from datetime import datetime
from rich import print

from database.database import Database
from schema import User, Link


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
                url TEXT NOT NULL,
                domain TEXT NOT NULL,
                description TEXT,
                tag TEXT,
                author_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
        """)
        self.connection.commit()

    def create_user(self, user: User):
        """Insert a new user."""
        self.cursor.execute(
            """
            INSERT INTO users (name, email)
            VALUES (?, ?)
        """,
            (user.name, user.email),
        )
        self.connection.commit()
        print("User created successfully.")

    def create_link(self, link: Link):
        """Insert a new link."""
        self.cursor.execute(
            """
            INSERT INTO links (url, domain, description, tag, author_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                link.url,
                link.domain,
                link.description,
                dumps(link.tag),
                link.author_id,
                link.created_at,
                link.updated_at,
            ),
        )
        self.connection.commit()
        print("Link created successfully.")

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
        return [
            {
                "link": Link(**dict(row), tag=loads(row["tag"])),
                "author": {"name": row["author_name"], "email": row["author_email"]},
            }
            for row in rows
        ]

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
