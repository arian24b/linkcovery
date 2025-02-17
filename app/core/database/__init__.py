from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings
from app.core.database.models import Base, User, Link
from app.core.database.crud import UserService, LinkService

engine = create_engine(f"sqlite:///{settings.DATABASE_NAME}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize services
session = SessionLocal()
user_service = UserService(session)
link_service = LinkService(session)

__all__ = ["user_service", "link_service", "User", "Link"]
