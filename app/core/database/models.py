from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base, validates

Base = declarative_base()


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tag = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

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
