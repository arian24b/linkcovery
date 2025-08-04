"""Database and data models for LinKCovery."""

from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Link(Base):
    """SQLAlchemy model for storing bookmark information."""

    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    domain = Column(String, nullable=False)
    description = Column(String, nullable=True, default="")
    tag = Column(String, nullable=False, default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"<Link(id={self.id}, url='{self.url}', domain='{self.domain}')>"


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

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate and clean description."""
        return v.strip() if v else ""

    @field_validator("tag")
    @classmethod
    def validate_tag(cls, v: str) -> str:
        """Validate and clean tag."""
        return v.strip() if v else ""

    def extract_domain(self) -> str:
        """Extract domain from the URL."""
        try:
            return urlparse(self.url).netloc.lower()
        except Exception:
            msg = "Could not extract domain from URL"
            raise ValueError(msg)


class LinkUpdate(BaseModel):
    """Pydantic model for updating existing links."""

    url: str | None = Field(None, description="New URL")
    description: str | None = Field(None, description="New description")
    tag: str | None = Field(None, description="New tag")
    is_read: bool | None = Field(None, description="New read status")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        """Validate URL format if provided."""
        if v is None:
            return v

        if not v or not isinstance(v, str):
            msg = "URL must be a string"
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
    def validate_strings(cls, v: str | None) -> str | None:
        """Validate and clean string fields."""
        return v.strip() if v else v


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
