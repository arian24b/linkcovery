from sqlite3 import connect, Row
from contextlib import contextmanager
from rich import print

from settings import settings


class Database:
    def __init__(self, db_name: str = settings.DATABASE_NAME):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        print("Database initialized.")

    def connect(self):
        try:
            self.connection = connect(self.db_name)
            self.connection.row_factory = Row
            self.cursor = self.connection.cursor()
            print("Connected to the database.")
        except Exception as e:
            print(f"[red]Failed to connect to the database: {e}[/red]")
            raise

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        else:
            print("No database connection to close.")

    @contextmanager
    def get_connection(self):
        try:
            self.connect()
            yield self.connection
        finally:
            self.close()
