from .database import Database
from .schema import User, Link
from .link import LinkDatabase
from app.core.logger import AppLogger


logger = AppLogger(__name__)

# Initialize database with settings
db = LinkDatabase()


def initialize_database(db):
    """
    Initializes the database by creating necessary tables and indexes.
    """
    db.get_connection()

    if db.is_initialized({"users", "links"}):
        logger.warning("Database initialization skipped. The database is already set up.")
    else:
        db.create_table()
        logger.warning("Database has been initialized successfully.")

    db.close_all()


initialize_database(db)

__all__ = ["Database", "User", "Link", "LinkDatabase"]
