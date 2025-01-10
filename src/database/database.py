from sqlite3 import connect, Row
from contextlib import contextmanager
from rich import print

from settings import settings


class Database:
    def __init__(self, db_name: str = settings.DATABASE_NAME):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        print("[blue]Database initialized.[/blue]")

    def connect(self):
        try:
            self.connection = connect(self.db_name)
            self.connection.row_factory = Row
            self.cursor = self.connection.cursor()
            print("[blue]Connected to the database.[/blue]")
        except Exception as e:
            print(f"[red]Failed to connect to the database: {e}[/red]")
            raise

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("[blue]Database connection closed.[/blue]")
        else:
            print("[yellow]No database connection to close.[/yellow]")

    @contextmanager
    def get_connection(self):
        try:
            self.connect()
            yield self.connection
        finally:
            self.close()

    @contextmanager
    def transaction(self):
        """
        Context manager for handling transactions.
        Commits the transaction if block succeeds, otherwise rolls back.
        """
        if not self.connection:
            self.connect()
        try:
            self.connection.execute("BEGIN")
            yield
            self.connection.commit()
            print("[green]Transaction committed.[/green]")
        except Exception as e:
            self.connection.rollback()
            print(f"[red]Transaction rolled back due to error: {e}[/red]")
            raise
