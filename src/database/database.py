from sqlite3 import connect, Row
from rich import print

from src.settengs import DATABASE_NAME


class Database:
    def __init__(self, db_name: str = DATABASE_NAME):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        print("Database initialized.")

    def connect(self):
        """Connect to SQLite database."""
        self.connection = connect(self.db_name)
        self.connection.row_factory = Row
        self.cursor = self.connection.cursor()
        print("Connected to the database.")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        else:
            print("No database connection to close.")
