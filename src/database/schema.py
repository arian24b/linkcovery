from pydantic import BaseModel, Field, EmailStr, HttpUrl
from datetime import datetime, UTC


class User(BaseModel):
    """A User model representing a user in the system.

    This model inherits from BaseModel and defines the basic user attributes
    including an optional ID, required name, and email address.

    Attributes:
        id (int|None): The unique identifier for the user. Auto-generated when None.
        name (str): The user's name. Must be at least 4 characters long.
        email (EmailStr): The user's email address in valid email format.

    Example:
        user = User(
            name="John Doe",
            email="john.doe@example.com"
        )
    """

    id: int | None = Field(None, description="User ID (autogenerated)")
    name: str = Field(..., min_length=4, description="Name of the user")
    email: EmailStr = Field(..., description="Email of the user")


class Link(BaseModel):
    """A Pydantic model representing a Link entity in the system.

    This model defines the structure and validation rules for link objects, including
    their URL, associated metadata, and relationships.

    Attributes:
        id (int|None): Unique identifier for the link.
        url (HttpUrl): The complete URL of the link.
        domain (str): The domain name extracted from the URL.
        description (str|None): Optional text description of the link's content.
        tag (list): List of tags associated with the link for categorization.
        author_id (int): ID reference to the user who created the link.
        is_read (bool): Flag indicating whether the link has been read, defaults to False.
        created_at (str): ISO format timestamp of when the link was created.
        updated_at (str): ISO format timestamp of the link's last modification.
    """

    id: int | None = Field(None, description="Unique identifier for the link")
    url: HttpUrl = Field(..., description="The URL of the link")
    domain: str = Field(..., description="Domain of the URL")
    description: str | None = Field(None, description="Description of the link")
    tag: list[str] = Field(default_factory=list, description="Tags associated with the link")
    author_id: int = Field(..., description="Foreign key to the User model")
    is_read: bool = Field(default=False, description="Whether the link has been read")
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat(), description="Last update timestamp")


class Config:
    allow_mutation = False
