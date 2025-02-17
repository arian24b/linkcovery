from typer import Typer, Option
from rich.table import Table

from app.core.logger import AppLogger
from app.core.database import user_service


logger = AppLogger(__name__)

app = Typer()


@app.command()
def list():
    """List all users"""
    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="green")

    for user in user_service.get_users():
        table.add_row(str(user.id), user.name, user.email)

    logger.print(table)


@app.command()
def create(name: str = Option(..., prompt=True), email: str = Option(..., prompt=True)):
    """Create new user"""
    user = user_service.create_user({"name": name, "email": email})
    logger.print(f"User created with ID: {user.id}")


@app.command()
def delete(user_id: int):
    """Delete user"""
    user_service.delete_user(user_id)
    logger.print(f"User with ID: {user_id} deleted")


@app.command()
def update(user_id: int, name: str = Option(None, prompt=True), email: str = Option(None, prompt=True)):
    """Update user information"""
    update_data = {}
    if name:
        update_data["name"] = name
    if email:
        update_data["email"] = email

    _ = user_service.update_user(user_id, update_data)
    logger.print(f"User with ID: {user_id} updated successfully")
