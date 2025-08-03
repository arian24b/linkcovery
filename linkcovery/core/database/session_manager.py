"""Improved database session management with dependency injection."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Protocol

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from linkcovery.core.database.models import Base
from linkcovery.core.settings import config_manager


class DatabaseSession(Protocol):
    """Protocol for database session dependency injection."""

    def get_session(self) -> Generator[Session]:
        """Get a database session."""
        ...


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create tables
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session]:
        """Context manager for database sessions with proper cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Factory function for dependency injection
def create_database_manager() -> DatabaseManager:
    """Create a database manager instance."""
    database_path = config_manager.config.database_path
    return DatabaseManager(f"sqlite:///{database_path}")


# Global instance for the application
db_manager = create_database_manager()
