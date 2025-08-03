"""Service interfaces and protocols for dependency injection."""

from typing import Any, Protocol

from app.core.database.models import Link, User


class UserServiceProtocol(Protocol):
    """Protocol for user service interface."""

    def create_user(self, user_data: dict[str, Any]) -> User | None:
        """Create a new user."""
        ...

    def get_user(self, user_id: int | None = None, user_email: str | None = None) -> User | None:
        """Get a user by ID or email."""
        ...

    def update_user(self, user_id: int, user_data: dict[str, Any]) -> bool:
        """Update a user."""
        ...

    def delete_user(self, user_id: int) -> None:
        """Delete a user."""
        ...

    def get_users(self) -> list[User]:
        """Get all users."""
        ...


class LinkServiceProtocol(Protocol):
    """Protocol for link service interface."""

    def create_link(self, **link_data: Any) -> Link | None:
        """Create a new link."""
        ...

    def get_link(self, link_id: int | None = None, link_url: str | None = None) -> Link | None:
        """Get a link by ID or URL."""
        ...

    def search_links(self, search_criteria: dict[str, Any]) -> list[Link]:
        """Search links based on criteria."""
        ...

    def update_link(self, link_id: int, **link_data: Any) -> bool:
        """Update a link."""
        ...

    def delete_link(self, link_id: int) -> None:
        """Delete a link."""
        ...

    def get_links(self) -> list[Link]:
        """Get all links."""
        ...

    def get_links_by_author(self, author_id: int, number: int | None = None) -> list[Link]:
        """Get links by author."""
        ...


class UserRepositoryProtocol(Protocol):
    """Protocol for user repository interface."""

    def create(self, user_data: dict[str, Any]) -> User:
        """Create a new user."""
        ...

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        ...

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        ...

    def update(self, user_id: int, user_data: dict[str, Any]) -> User | None:
        """Update user."""
        ...

    def delete(self, user_id: int) -> None:
        """Delete user."""
        ...

    def get_all(self) -> list[User]:
        """Get all users."""
        ...


class LinkRepositoryProtocol(Protocol):
    """Protocol for link repository interface."""

    def create(self, link_data: dict[str, Any]) -> Link:
        """Create a new link."""
        ...

    def get_by_id(self, link_id: int) -> Link | None:
        """Get link by ID."""
        ...

    def get_by_url(self, url: str) -> Link | None:
        """Get link by URL."""
        ...

    def search(self, search_criteria: dict[str, Any]) -> list[Link]:
        """Search links."""
        ...

    def update(self, link_id: int, link_data: dict[str, Any]) -> Link | None:
        """Update link."""
        ...

    def delete(self, link_id: int) -> None:
        """Delete link."""
        ...

    def get_all(self) -> list[Link]:
        """Get all links."""
        ...

    def get_links_by_author(self, author_id: int, number: int | None = None) -> list[Link]:
        """Get links by author."""
        ...
