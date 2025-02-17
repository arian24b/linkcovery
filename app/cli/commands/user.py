from typer import Typer, Option
from rich.table import Table

from app.core.logger import AppLogger
from app.core.database import user_service


logger = AppLogger(__name__)
app = Typer()


@app.command(name="create", help="This command creates a new user with the specified name and email.")
def create(name: str = Option(..., prompt=True), email: str = Option(..., prompt=True)):
    """Create a new user.

    This command creates a new user with the specified name and email.

    Args:
        name (str): The name of the user. Will be prompted if not provided.
        email (str): The email address of the user. Will be prompted if not provided.

    Returns:
        None: Prints the created user's ID to the console.

    Example:
        $ linkcovery user create
        Name: John Doe
        Email: john@example.com
        User created with ID: 123
    """
    user = user_service.create_user({"name": name, "email": email})
    logger.print(f"{name} your account has been created with ID: {user.id} and Email: {email}")


@app.command(name="read", help="This command fetches a user by ID.")
def read_user(user_id: int):
    """Get and display user information in a table format.
    This function retrieves user information by ID and displays it in a formatted table
    with columns for ID, Name, and Email using the rich library's Table component.
    Args:
        user_id (int): The unique identifier of the user to retrieve.
    Returns:
        None: Prints the formatted table to the console using logger.
    Example:
        >>> get(1)
        ┌────┬──────┬───────┐
        │ ID │ Name │ Email │
        ├────┼──────┼───────┤
        │ 1  │ John │ j@e.c │
        └────┴──────┴───────┘
    """
    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Email", style="green")

    user = user_service.get_user(user_id)
    table.add_row(str(user.id), user.name, user.email)

    logger.print(table)


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


@app.command()
def delete(user_id: int):
    """Delete user"""
    user_service.delete_user(user_id)
    logger.print(f"User with ID: {user_id} deleted")


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
