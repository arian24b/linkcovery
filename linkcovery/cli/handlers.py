"""Link command handlers implementing the command handler pattern."""

from abc import ABC, abstractmethod
from typing import Any

from linkcovery.core.database.crud import LinkService
from linkcovery.core.database.session_manager import DatabaseManager
from linkcovery.core.exceptions import EntityNotFoundError, LinKCoveryError, ServiceError
from linkcovery.core.logger import Logger


class CommandResult:
    """Represents the result of a command execution."""

    def __init__(self, success: bool, message: str, data: Any = None) -> None:
        self.success = success
        self.message = message
        self.data = data


class BaseCommandHandler(ABC):
    """Base class for command handlers."""

    def __init__(self, link_service) -> None:
        self.link_service = link_service
        self.logger = Logger(self.__class__.__name__)

    @abstractmethod
    def handle(self, *args, **kwargs) -> CommandResult:
        """Handle the command execution."""

    def _handle_error(self, error: Exception, operation: str) -> CommandResult:
        """Standardized error handling."""
        if isinstance(error, LinKCoveryError):
            error_msg = error.message
            self.logger.error(error_msg)
        else:
            error_msg = f"Failed to {operation}: {error!s}"
            self.logger.exception(error_msg)

        return CommandResult(success=False, message=error_msg)

    def _validate_required_params(self, **params) -> CommandResult | None:
        """Validate required parameters."""
        for key, value in params.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                return CommandResult(success=False, message=f"Parameter '{key}' is required")
        return None


class CreateLinkHandler(BaseCommandHandler):
    """Handler for creating new links."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager)

    def execute(self, link_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new link with validation."""
        with self.db_manager.get_session() as session:
            user_service = UserService(session)
            link_service = LinkService(session)

            # Validate author exists
            author_email = link_data.get("author_email")
            if not author_email:
                msg = "Author email is required"
                raise ServiceError(msg)

            author = user_service.get_user_by_email(author_email)
            if not author:
                msg = "User"
                raise EntityNotFoundError(msg, author_email)

            # Prepare link data
            tags = link_data.get("tags", [])
            tag_string = ", ".join(tags) if isinstance(tags, list) else tags or ""

            link_creation_data = {
                "url": link_data["url"],
                "domain": link_data.get("domain", ""),
                "description": link_data.get("description", ""),
                "tag": tag_string,
                "author_id": author.id,
                "is_read": link_data.get("is_read", False),
            }

            link = link_service.create_link(link_creation_data)

            return {"success": True, "link_id": link.id, "message": f"Link added with ID: {link.id}"}


class ListLinksHandler(BaseCommandHandler):
    """Handler for listing all links."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager)

    def execute(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """List all links."""
        with self.db_manager.get_session() as session:
            link_service = LinkService(session)

            links = link_service.get_all_links()

            if not links:
                return {"success": True, "links": [], "message": "No links found"}

            link_data = []
            for link in links:
                link_data.append(
                    {
                        "id": link.id,
                        "url": link.url,
                        "domain": link.domain,
                        "description": link.description,
                        "tags": link.tag,
                        "is_read": link.is_read,
                        "author_name": link.author.name if link.author else "Unknown",
                    },
                )

            return {"success": True, "links": link_data, "count": len(link_data)}


class SearchLinksHandler(BaseCommandHandler):
    """Handler for searching links with filters."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager)

    def execute(self, search_criteria: dict[str, Any]) -> dict[str, Any]:
        """Search links based on criteria."""
        with self.db_manager.get_session() as session:
            link_service = LinkService(session)

            # Filter out None/empty values
            filtered_criteria = {k: v for k, v in search_criteria.items() if v not in [None, [], ""]}

            links = link_service.search_links(filtered_criteria)

            if not links:
                return {"success": True, "links": [], "message": "No matching links found"}

            link_data = []
            for link in links:
                link_data.append(
                    {
                        "id": link.id,
                        "url": link.url,
                        "domain": link.domain,
                        "description": link.description,
                        "tags": link.tag,
                        "is_read": link.is_read,
                        "author_name": link.author.name if link.author else "Unknown",
                    },
                )

            return {"success": True, "links": link_data, "count": len(link_data)}


class DeleteLinkHandler(BaseCommandHandler):
    """Handler for deleting links."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager)

    def execute(self, link_id: int) -> dict[str, Any]:
        """Delete a link by ID."""
        with self.db_manager.get_session() as session:
            link_service = LinkService(session)

            # Check if link exists
            existing_link = link_service.get_link_by_id(link_id)
            if not existing_link:
                msg = "Link"
                raise EntityNotFoundError(msg, str(link_id))

            success = link_service.delete_link(link_id)

            if success:
                return {"success": True, "message": f"Link with ID {link_id} has been deleted"}
            return {"success": False, "message": f"Failed to delete link with ID {link_id}"}


class UpdateLinkHandler(BaseCommandHandler):
    """Handler for updating link details."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager)

    def execute(self, link_id: int, update_data: dict[str, Any]) -> dict[str, Any]:
        """Update a link by ID."""
        with self.db_manager.get_session() as session:
            link_service = LinkService(session)

            # Check if link exists
            existing_link = link_service.get_link_by_id(link_id)
            if not existing_link:
                msg = "Link"
                raise EntityNotFoundError(msg, str(link_id))

            # Process tags if provided
            if "tags" in update_data and isinstance(update_data["tags"], list):
                update_data["tag"] = ", ".join(update_data["tags"])
                del update_data["tags"]

            # Filter out None values
            filtered_data = {k: v for k, v in update_data.items() if v is not None}

            if not filtered_data:
                return {"success": True, "message": "No changes to apply"}

            updated_link = link_service.update_link(link_id, filtered_data)

            if updated_link:
                return {"success": True, "message": f"Link with ID {link_id} has been updated"}
            return {"success": False, "message": f"Failed to update link with ID {link_id}"}


class MarkLinksAsReadHandler(BaseCommandHandler):
    """Handler for marking links as read."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager)

    def execute(self, author_id: int, number: int = 3) -> dict[str, Any]:
        """Mark links as read for an author."""
        with self.db_manager.get_session() as session:
            link_service = LinkService(session)
            user_service = UserService(session)

            # Validate author exists
            author = user_service.get_user_by_id(author_id)
            if not author:
                msg = "User"
                raise EntityNotFoundError(msg, str(author_id))

            links = link_service.get_links_by_author(author_id, number)

            if not links:
                return {"success": True, "message": "No links found to update", "updated_links": []}

            link_ids = [link.id for link in links if link.id is not None]
            link_service.update_is_read_for_links(link_ids)

            updated_links = []
            for link in links:
                updated_links.append({"id": link.id, "url": link.url, "marked_as_read": True})

            return {
                "success": True,
                "message": f"Marked {len(updated_links)} links as read",
                "updated_links": updated_links,
            }
