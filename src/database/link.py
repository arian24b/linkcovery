from sqlite3 import IntegrityError
from json import dumps, loads
from datetime import datetime, UTC
from rich import print

from .database import Database
from .schema import User, Link


class LinkDatabase(Database):
    def create_table(self) -> None:
        """Create users and links tables."""
        with self.transaction() as cursor:
            # Create the users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                )
            """)

            # Create the links table with a foreign key to users
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    domain TEXT NOT NULL,
                    description TEXT,
                    tag TEXT,
                    author_id INTEGER NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (author_id) REFERENCES users (id)
                )
            """)

            # Create an index on the domain column to speed up domain-based searches
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_links_domain ON links (domain)
            """)

            # Create an index on the created_at column to speed up sorting
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_links_created_at ON links (created_at)
            """)
        print("[blue]Tables and indexes created successfully.[/blue]")

    def create_user(self, user: User) -> int | None:
        """Insert a new user."""
        try:
            with self.transaction() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (name, email)
                    VALUES (?, ?)
                    """,
                    (user.name, user.email),
                )
                user_id = cursor.lastrowid
                print("[green]User created successfully.[/green]")
                return user_id
        except IntegrityError as e:
            print(f"[red]Error: User with email {user.email} already exists. ({e})[/red]")
            # Retrieve the existing user's ID
            if existing_user := self.get_user_by_email(user.email):
                return existing_user.id
            return None
        except Exception as e:
            print(f"[red]Unexpected error occurred while creating user: {e}[/red]")
            return None

    def create_link(self, link: Link) -> int | None:
        """Insert a new link."""
        try:
            with self.transaction() as cursor:
                cursor.execute(
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
                link_id = cursor.lastrowid
                print("[green]Link created successfully.[/green]")
                return link_id
        except IntegrityError as e:
            print(f"[red]Error: Link with URL {link.url} already exists or invalid author ID. ({e})[/red]")
            return None
        except Exception as e:
            print(f"[red]Unexpected error occurred while creating link: {e}[/red]")
            return None

    def create_user_and_link(self, user: User, link: Link) -> bool:
        """
        Create a user and a link atomically.
        If either operation fails, neither is committed.
        """
        try:
            user_id = self.create_user(user)
            if user_id is None:
                raise Exception("Failed to create or retrieve user.")

            link.author_id = user_id
            self.create_link(link)
            return True
        except Exception as e:
            print(f"[red]Failed to create user and link atomically: {e}[/red]")
            return False

    def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""
        try:
            with self.transaction() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()
                if row:
                    return User(**dict(row))
                return None
        except Exception as e:
            print(f"[red]Unexpected error occurred while retrieving user: {e}[/red]")
            return None

    def read_users(self) -> list[User]:
        """Retrieve all users."""
        try:
            with self.transaction() as cursor:
                cursor.execute("SELECT * FROM users")
                rows = cursor.fetchall()
                return [User(**dict(row)) for row in rows]
        except Exception as e:
            print(f"[red]Unexpected error occurred while reading users: {e}[/red]")
            return []

    def read_links_with_authors(self) -> list[dict]:
        """Retrieve all links with their authors."""
        with self.transaction() as cursor:
            cursor.execute("""
                SELECT links.*, users.name as author_name, users.email as author_email
                FROM links
                JOIN users ON links.author_id = users.id
            """)
            rows = cursor.fetchall()

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

    def read_link(self, link_id: int) -> Link | None:
        """Retrieve a specific link by ID."""
        with self.transaction() as cursor:
            cursor.execute("SELECT * FROM links WHERE id = ?", (link_id,))
            row = cursor.fetchone()
        if row:
            row_dict = dict(row)
            # Extract and parse the tag, then remove it from the row_dict
            tag_json = row_dict.pop("tag")
            return Link(**row_dict, tag=loads(tag_json))
        return None

    def update_link(self, link_id: int, updated_link: Link) -> bool:
        """Update a link by ID."""
        try:
            updated_link.updated_at = datetime.now(UTC).isoformat()
            with self.transaction() as cursor:
                cursor.execute(
                    """
                    UPDATE links
                    SET url = ?, domain = ?, description = ?, tag = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        str(updated_link.url),
                        updated_link.domain,
                        updated_link.description,
                        dumps(updated_link.tag),
                        updated_link.updated_at,
                        link_id,
                    ),
                )
                if cursor.rowcount == 0:
                    print(f"[yellow]No link found with ID {link_id}. Nothing was updated.[/yellow]")
                    return False
                else:
                    cursor.connection.commit()
                    print("[green]Link updated successfully.[/green]")
                    return True
        except IntegrityError as e:
            print(f"[red]Error: Duplicate URL or invalid update data. ({e})[/red]")
            return False
        except Exception as e:
            print(f"[red]Unexpected error occurred while updating link: {e}[/red]")
            return False

    def delete_link(self, link_id: int) -> None:
        """Delete a link by ID."""
        try:
            with self.transaction() as cursor:
                cursor.execute("DELETE FROM links WHERE id = ?", (link_id,))
                if cursor.rowcount == 0:
                    print(f"[yellow]No link found with ID {link_id}. Nothing was deleted.[/yellow]")
                else:
                    cursor.connection.commit()
                    print("[green]Link deleted successfully.[/green]")
        except Exception as e:
            print(f"[red]Unexpected error occurred while deleting link: {e}[/red]")

    def search_links(
        self,
        domain: str | None = None,
        tags: list[str] | None = None,
        description: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "ASC",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Link]:
        """Search for links by domain, tags, or description with sorting and pagination."""
        try:
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

            # Filter by tags using JSON1 extension
            if tags:
                # For each tag, ensure it exists in the JSON array
                tag_conditions = " AND ".join(
                    ["EXISTS (SELECT 1 FROM json_each(links.tag) WHERE json_each.value = ?)" for _ in tags]
                )
                query += f" {tag_conditions}"
                parameters.extend(tags)

            # Validate sort_by field
            allowed_sort_fields = {"created_at", "updated_at", "domain"}
            if sort_by not in allowed_sort_fields:
                raise ValueError(f"Invalid sort_by field: {sort_by}. Allowed fields: {allowed_sort_fields}")

            # Validate sort_order
            sort_order = sort_order.upper()
            if sort_order not in {"ASC", "DESC"}:
                raise ValueError("Invalid sort_order; use 'ASC' or 'DESC'")

            # Append sorting
            query += f" ORDER BY {sort_by} {sort_order}"

            # Append pagination
            query += " LIMIT ? OFFSET ?"
            parameters.extend([limit, offset])

            # Execute the query
            with self.transaction() as cursor:
                cursor.execute(query, parameters)
                rows = cursor.fetchall()

            # Convert rows to Link objects
            links = []
            for row in rows:
                row_dict = dict(row)
                row_dict["tag"] = loads(row_dict["tag"]) if row_dict["tag"] else []
                links.append(Link(**row_dict))

            return links
        except ValueError as ve:
            print(f"[red]Validation error: {ve}[/red]")
            return []
        except Exception as e:
            print(f"[red]Unexpected error occurred during search: {e}[/red]")
            return []

    def read_links(self, limit: int = 3) -> list[Link]:
        """Retrieve a specific number of links."""
        with self.transaction() as cursor:
            cursor.execute("SELECT * FROM links ORDER BY created_at LIMIT ?", (limit,))
            rows = cursor.fetchall()

        # Convert rows to Link objects
        links = []
        for row in rows:
            row_dict = dict(row)
            row_dict["tag"] = loads(row_dict["tag"]) if row_dict["tag"] else []
            links.append(Link(**row_dict))

        return links

    def update_is_read_for_links(self, link_ids: list[int]) -> None:
        """Update the 'is_read' field for a list of links."""
        try:
            with self.transaction() as cursor:
                cursor.executemany(
                    """
                    UPDATE links
                    SET is_read = 1
                    WHERE id = ?
                    """,
                    [(link_id,) for link_id in link_ids],  # List of link IDs
                )
            print(f"[green]Successfully updated 'is_read' for {len(link_ids)} links.[/green]")
        except Exception as e:
            print(f"[red]Failed to update 'is_read' for links: {e}[/red]")
