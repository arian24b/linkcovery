from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database.crud import LinkService, UserService
from app.core.database.models import Base, Link, User
from app.core.settings import settings

engine = create_engine(f"sqlite:///{settings.DATABASE_NAME}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize services
session = SessionLocal()
user_service = UserService(session)
link_service = LinkService(session)

__all__ = ["Link", "User", "link_service", "user_service"]
