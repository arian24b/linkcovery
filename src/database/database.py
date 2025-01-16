from sqlite3 import connect, Row, Connection
from contextlib import contextmanager
from rich import print
from queue import Queue
from threading import Lock

from settings import settings


class Database:
    def __init__(self, pool_size: int = 5):
        self.db_name = settings.DATABASE_NAME
        self.pool_size = pool_size
        self.pool = Queue(maxsize=self.pool_size)
        self.lock = Lock()
        self._initialize_pool()
        print(f"[blue]Database initialized with a connection pool of size {self.pool_size}.[/blue]")

    def _initialize_pool(self):
        """Initialize the connection pool with a fixed number of connections."""
        for _ in range(self.pool_size):
            conn = connect(self.db_name, check_same_thread=False)
            conn.row_factory = Row
            self.pool.put(conn)

    def close_all(self):
        """Close all connections in the pool."""
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()
        print("[blue]All database connections have been closed.[/blue]")

    @contextmanager
    def get_connection(self) -> Connection:
        """
        Context manager to acquire a database connection from the pool.
        Ensures the connection is returned to the pool after use.
        """
        conn = self.pool.get()
        try:
            yield conn
        finally:
            self.pool.put(conn)

    @contextmanager
    def transaction(self):
        """
        Context manager for handling transactions.
        Commits the transaction if block succeeds, otherwise rolls back.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("BEGIN")
                yield cursor
                conn.commit()
                print("[green]Transaction committed.[/green]")
            except Exception as e:
                conn.rollback()
                print(f"[red]Transaction rolled back due to error: {e}[/red]")
                raise

    def is_initialized(self, required_tables: set) -> bool:
        """
        Checks if the essential tables ('users' and 'links') exist in the database.

        Returns:
            bool: True if both tables exist, False otherwise.
        """
        existing_tables = set()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            existing_tables = {table["name"] for table in tables}

        if is_init := required_tables.issubset(existing_tables):
            print("[blue]Database is already initialized.[/blue]")
        else:
            print("[yellow]Database is not initialized yet.[/yellow]")

        return is_init

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and close all connections."""
        self.close_all()
