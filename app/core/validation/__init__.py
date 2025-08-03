"""Input validation schemas using Pydantic for type safety and validation."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator


class CreateUserRequest(BaseModel):
    """Schema for user creation requests."""

    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")

    class Config:
        json_schema_extra = {"example": {"name": "John Doe", "email": "john.doe@example.com"}}


class UpdateUserRequest(BaseModel):
    """Schema for user update requests."""

    name: str | None = Field(None, min_length=1, max_length=100, description="User's full name")
    email: EmailStr | None = Field(None, description="User's email address")

    @validator("name", "email")
    def not_empty_string(self, v):
        if v is not None and isinstance(v, str) and not v.strip():
            msg = "Field cannot be empty string"
            raise ValueError(msg)
        return v


class CreateLinkRequest(BaseModel):
    """Schema for link creation requests."""

    url: HttpUrl = Field(..., description="URL of the link")
    domain: str | None = Field(None, max_length=255, description="Domain of the link")
    author_email: EmailStr = Field(..., description="Email of the author")
    description: str | None = Field("", max_length=1000, description="Description of the link")
    tags: list[str] | None = Field(default_factory=list, description="Tags associated with the link")
    is_read: bool = Field(False, description="Mark the link as read or unread")

    @validator("tags")
    def validate_tags(self, v):
        if v is not None:
            # Remove empty tags and limit tag length
            return [tag.strip() for tag in v if tag.strip() and len(tag.strip()) <= 50][:10]
        return []

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "domain": "example.com",
                "author_email": "john.doe@example.com",
                "description": "An example website",
                "tags": ["example", "website"],
                "is_read": False,
            },
        }


class UpdateLinkRequest(BaseModel):
    """Schema for link update requests."""

    url: HttpUrl | None = Field(None, description="URL of the link")
    domain: str | None = Field(None, max_length=255, description="Domain of the link")
    description: str | None = Field(None, max_length=1000, description="Description of the link")
    tags: list[str] | None = Field(None, description="Tags associated with the link")
    is_read: bool | None = Field(None, description="Mark the link as read or unread")

    @validator("tags")
    def validate_tags(self, v):
        if v is not None:
            # Remove empty tags and limit tag length
            return [tag.strip() for tag in v if tag.strip() and len(tag.strip()) <= 50][:10]
        return v

    @validator("domain", "description")
    def not_empty_string(self, v):
        if v is not None and isinstance(v, str) and not v.strip():
            msg = "Field cannot be empty string"
            raise ValueError(msg)
        return v


class SearchLinksRequest(BaseModel):
    """Schema for link search requests."""

    domain: str | None = Field(None, max_length=255, description="Filter by domain")
    url: str | None = Field(None, description="Filter by URL")
    tags: list[str] | None = Field(default_factory=list, description="Tags to filter by")
    description: str | None = Field(None, description="Filter by description")
    sort_by: str | None = Field(None, description="Field to sort by")
    sort_order: str = Field("ASC", regex="^(ASC|DESC)$", description="Sort order: ASC or DESC")
    limit: int = Field(3, ge=1, le=100, description="Number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    is_read: bool | None = Field(None, description="Filter by read status")

    @validator("sort_by")
    def validate_sort_by(self, v):
        allowed_fields = ["created_at", "updated_at", "domain", "url", "description"]
        if v is not None and v not in allowed_fields:
            msg = f"sort_by must be one of: {', '.join(allowed_fields)}"
            raise ValueError(msg)
        return v


class ImportLinksRequest(BaseModel):
    """Schema for link import requests."""

    file_path: str = Field(..., description="Path to the file to import")
    author_id: int = Field(..., gt=0, description="ID of the author to associate with imported links")

    @validator("file_path")
    def validate_file_path(self, v):
        allowed_extensions = [".txt", ".csv", ".json"]
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            msg = f"File must have one of these extensions: {', '.join(allowed_extensions)}"
            raise ValueError(msg)
        return v


class ExportLinksRequest(BaseModel):
    """Schema for link export requests."""

    format: str = Field("json", regex="^(json|csv)$", description="Export format")
    output: str | None = Field(None, description="Output file path")
    author_id: int | None = Field(None, gt=0, description="ID of author to export links for")

    @validator("output")
    def validate_output_path(self, v, values):
        if v is None:
            format_type = values.get("format", "json")
            return f"links_export.{format_type}"
        return v


class ExportUsersRequest(BaseModel):
    """Schema for user export requests."""

    format: str = Field("json", regex="^(json)$", description="Export format")
    output: str | None = Field(None, description="Output file path")

    @validator("output")
    def validate_output_path(self, v, values):
        if v is None:
            format_type = values.get("format", "json")
            return f"users_export.{format_type}"
        return v


class LinkIdRequest(BaseModel):
    """Schema for single link ID requests."""

    link_id: int = Field(..., gt=0, description="ID of the link")


class UserIdRequest(BaseModel):
    """Schema for single user ID requests."""

    user_id: int = Field(..., gt=0, description="ID of the user")


class MarkLinksAsReadRequest(BaseModel):
    """Schema for marking links as read."""

    author_id: int = Field(..., gt=0, description="ID of the author")
    number: int = Field(3, ge=1, le=50, description="Number of links to mark as read")
