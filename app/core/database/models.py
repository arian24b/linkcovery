from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship, validates

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    links = relationship("Link", back_populates="author")

    @validates("name")
    def validate_name(self, key, value):
        if len(value) < 4:
            msg = "Name must be at least 4 characters long."
            raise ValueError(msg)
        return value

    @validates("email")
    def validate_email(self, key, value):
        return value


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tag = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    author = relationship("User", back_populates="links")

    @validates("url")
    def validate_url(self, key, value):
        if not value.startswith("http://") and not value.startswith("https://"):
            msg = "Invalid URL format."
            raise ValueError(msg)
        return value

    @validates("domain")
    def validate_domain(self, key, value):
        if not value or len(value.strip()) == 0:
            msg = "Domain cannot be empty or just whitespace."
            raise ValueError(msg)
        if "." not in value:
            msg = "Domain must contain at least one dot."
            raise ValueError(msg)
        return value.lower()

    @validates("author_id")
    def validate_author(self, key, value):
        if not value:
            msg = "Author ID is required."
            raise ValueError(msg)
        return value
