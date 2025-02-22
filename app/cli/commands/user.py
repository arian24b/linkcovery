from typer import Typer, Option
from rich.table import Table

from app.core.logger import AppLogger
from app.core.database import user_service

logger = AppLogger(__name__)
app = Typer()


@app.command(name="create", help="Create a new user with the specified name and email.")
def create(name: str = Option(..., prompt=True), email: str = Option(..., prompt=True)):
    try:
        user = user_service.create_user({"name": name, "email": email})
        logger.print(f"{name}, your account has been created with ID: {user.id} and Email: {email}")
    except Exception as e:
        logger.error(f"Error creating user: {e}")


@app.command(name="read", help="Fetch a user by ID.")
def read_user(user_id: int):
    if not (user := user_service.get_user(user_id)):
        logger.error(f"No user found with ID {user_id}")
        return
    table = Table(title="User")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="green")
    table.add_row(str(user.id), user.name, user.email)
    logger.print(table)


@app.command()
def update(user_id: int, name: str = Option(None, prompt=True), email: str = Option(None, prompt=True)):
    update_data = {}
    if name:
        update_data["name"] = name
    if email:
        update_data["email"] = email

    if not update_data:
        logger.warning("No updates provided.")
        return

    if user_service.update_user(user_id, update_data):
        logger.print(f"User with ID: {user_id} updated successfully")
    else:
        logger.error(f"User with ID: {user_id} not found.")


@app.command()
def delete(user_id: int):
    user_service.delete_user(user_id)
    logger.print(f"User with ID: {user_id} deleted")


@app.command()
def list():
    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="green")

    if not (users := user_service.get_users()):
        logger.print("No users found.")
        return
    for user in users:
        table.add_row(str(user.id), user.name, user.email)
    logger.print(table)
