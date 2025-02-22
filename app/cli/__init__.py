from typer import Typer

from app.cli.commands import user, link, import_export
from app.core.settings import settings


# Initialize Typer for potential future CLI enhancements
cli_app = Typer(
    name=settings.APP_NAME,
    no_args_is_help=True,
    help=f"{settings.APP_NAME}, Bookmark management CLI Application",
)

cli_app.add_typer(user.app, name="user")
cli_app.add_typer(link.app, name="link")
cli_app.add_typer(import_export.app, name="db")
