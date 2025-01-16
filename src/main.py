from rich import print
from database import LinkDatabase
from typer import Typer

# Initialize Typer for potential future CLI enhancements
app = Typer(help="Linkcovery CLI Application")


def initialize_database():
    """
    Initializes the database by creating necessary tables and indexes.
    """
    db = LinkDatabase()

    if db.is_initialized({"users", "links"}):
        print("[yellow]Database initialization skipped. The database is already set up.[/yellow]")
    else:
        db.create_table()
        print("[green]Database has been initialized successfully.[/green]")

    db.close_all()


# Main Script for Initialization
if __name__ == "__main__":
    initialize_database()
