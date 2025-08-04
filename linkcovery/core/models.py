"""Database models for LinKCovery."""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Link(Base):
    """Link model for storing bookmark information."""

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
