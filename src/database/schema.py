from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: Optional[int] = Field(None, description="User ID (autogenerated)")
    name: str = Field(..., min_length=4, description="Name of the user")
    email: EmailStr = Field(..., description="Email of the user")


class Link(BaseModel):
    id: Optional[int] = Field(None, description="Unique identifier for the link")
    url: HttpUrl = HttpUrl(..., description="The URL of the link")
    domain: str = Field(..., description="Domain of the URL")
    description: Optional[str] = Field(None, description="Description of the link")
    tag: list = Field(default_factory=list, description="Tags associated with the link")
    author_id: int = Field(..., description="Foreign key to the User model")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Last update timestamp")