from typer import Typer

from database import LinkDatabase
from logger import Logger
from settings import settings

logger = Logger(__name__)

# Initialize database with settings
db = LinkDatabase()
db.get_connection()

# Initialize Typer for potential future CLI enhancements
app = Typer(
    name=settings.APP_NAME,
    no_args_is_help=True,
    help=f"{settings.APP_NAME} CLI Application",
    rich_markup_mode=True,
)


def initialize_database():
    """
    Initializes the database by creating necessary tables and indexes.
    """
    db = LinkDatabase()

    if db.is_initialized({"users", "links"}):
        logger.warning("Database initialization skipped. The database is already set up.")
    else:
        db.create_table()
        logger.warning("Database has been initialized successfully.")

    db.close_all()


if __name__ == "__main__":
    initialize_database()
