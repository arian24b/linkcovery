from typer import Typer, Option, Exit
from rich.table import Table

from app.core.logger import AppLogger
from app.core.models import User
from app.core.models import db


logger = AppLogger(__name__)

app = Typer()


@app.command()
def list():
    """List all users"""
    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="green")

    for user in db.read_users():
        table.add_row(str(user.id), user.name, user.email)

    logger.print(table)


@app.command()
def create(name: str = Option(..., prompt=True), email: str = Option(..., prompt=True)):
    """Create new user"""
    try:
        user = db.create_user(User(name=name, email=email))
        logger.success(f"User created with ID: {user.id}")
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise Exit(code=1)
