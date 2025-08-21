"""Database and data models for LinKCovery."""

from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Boolean, Column, Index, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Database model for storing bookmark information
class Link(Base):
    """SQLAlchemy model for storing bookmark information."""

    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    domain = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True, default="")
    tag = Column(String, nullable=False, default="", index=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(String, nullable=False, index=True)
    updated_at = Column(String, nullable=False)

    __table_args__ = (
        # Composite indexes for common query patterns
        Index("idx_domain_is_read", "domain", "is_read"),
        Index("idx_tag_is_read", "tag", "is_read"),
        Index("idx_created_at_desc", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Link(id={self.id}, url='{self.url}', domain='{self.domain}')>"


# Schema for link services
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
    def validate_description(cls, v: str) -> str | None:
        """Validate and clean description and tag."""
        return v.strip() if v else None


class LinkUpdate(BaseModel):
    """Pydantic model for updating existing links."""

    url: str | None = Field(None, description="The URL to bookmark")
    description: str | None = Field(None, description="Optional description for the link")
    tag: str | None = Field(None, description="Tag to categorize the link")
    is_read: bool | None = Field(None, description="Whether the link has been read")

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
        # Return empty string as-is to allow clearing fields
        return v.strip()


class LinkFilter(BaseModel):
    """Pydantic model for filtering links."""

    query: str = Field("", description="Search query for URL, description, or tags")
    domain: str = Field("", description="Filter by domain")
    tag: str = Field("", description="Filter by tag")
    is_read: bool | None = Field(None, description="Filter by read status")
    limit: int = Field(50, description="Maximum number of results", ge=1, le=1000)


class LinkExport(BaseModel):
    """Pydantic model for exporting link data."""

    id: int
    url: str
    domain: str
    description: str
    tag: str
    is_read: bool
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
            created_at=link.created_at,
            updated_at=link.updated_at,
        )
