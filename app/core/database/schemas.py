from pydantic import BaseModel, EmailStr, HttpUrl


class UserCreate(BaseModel):
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


class LinkCreate(BaseModel):
    url: HttpUrl
    description: str | None = None
    tag: list[str]
    created_at: str
    updated_at: str
    author_id: int

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None

    class Config:
        orm_mode = True


class LinkUpdate(BaseModel):
    url: HttpUrl | None = None
    description: str | None = None
    tag: list[str] | None = None
    is_read: None | None = None

    class Config:
        orm_mode = True
