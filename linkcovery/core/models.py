"""Database and data models for LinKCovery."""

from dataclasses import dataclass
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


@dataclass
class Link:
    """Link model for database storage."""

    id: int
    url: str
    domain: str
    description: str
    tag: str
    is_read: bool
    preview_url: str
    created_at: str
    updated_at: str


class LinkCreate(BaseModel):
    """Pydantic model for creating new links."""

    url: str = Field(..., description="The URL to bookmark")
    description: str = Field("", description="Optional description for the link")
    tag: str = Field("", description="Tag to categorize the link")
    is_read: bool = Field(False, description="Whether the link has been read")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v or not isinstance(v, str):
            msg = "URL is required and must be a string"
            raise ValueError(msg)

        v = v.strip()
        if not v.startswith(("http://", "https://")):
            msg = "URL must start with http:// or https://"
            raise ValueError(msg)

        try:
            result = urlparse(v)
            if not result.netloc:
                msg = "URL must have a valid domain"
                raise ValueError(msg)
        except Exception as e:
            msg = f"Invalid URL format: {e}"
            raise ValueError(msg)

        return v

    @field_validator("description", "tag")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate and clean description and tag."""
        return v.strip() if v else ""


class LinkUpdate(BaseModel):
    """Pydantic model for updating existing links."""

    url: str | None = Field(None, description="The URL to bookmark")
    description: str | None = Field(None, description="Optional description for the link")
    tag: str | None = Field(None, description="Tag to categorize the link")
    is_read: bool | None = Field(None, description="Whether the link has been read")
    preview_url: str | None = Field(None, description="Preview image URL for the link")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        """Validate URL format when provided."""
        if v is None:
            return v

        if not v or not isinstance(v, str):
            msg = "URL is required and must be a string"
            raise ValueError(msg)

        v = v.strip()
        if not v.startswith(("http://", "https://")):
            msg = "URL must start with http:// or https://"
            raise ValueError(msg)

        try:
            result = urlparse(v)
            if not result.netloc:
                msg = "URL must have a valid domain"
                raise ValueError(msg)
        except Exception as e:
            msg = f"Invalid URL format: {e}"
            raise ValueError(msg)

        return v

    @field_validator("description", "tag")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate and clean description and tag when provided."""
        if v is None:
            return v
        return v.strip()


class LinkFilter(BaseModel):
    """Pydantic model for filtering links."""

    query: str = Field("", description="Search query for URL, description, or tags")
    domain: str = Field("", description="Filter by domain")
    tag: str = Field("", description="Filter by tag")
    is_read: bool | None = Field(None, description="Filter by read status")
    sort: str = Field("newest", description="Sort order: newest, oldest, domain, read_status")
    offset: int = Field(0, description="Number of records to skip", ge=0)
    limit: int = Field(50, description="Maximum number of results", ge=1, le=1000)


class LinkExport(BaseModel):
    """Pydantic model for exporting link data."""

    id: int
    url: str
    domain: str
    description: str
    tag: str
    is_read: bool
    preview_url: str
    created_at: str
    updated_at: str

    @classmethod
    def from_db_link(cls, link: Link) -> "LinkExport":
        """Create export model from database link."""
        return cls(
            id=link.id,
            url=link.url,
            domain=link.domain,
            description=link.description or "",
            tag=link.tag or "",
            is_read=link.is_read,
            preview_url=link.preview_url or "",
            created_at=link.created_at,
            updated_at=link.updated_at,
        )
