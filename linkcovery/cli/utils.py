"""CLI utilities and decorators for LinKCovery."""

import functools
from collections.abc import Callable
from typing import Any

from rich.console import Console
from typer import Exit

from linkcovery.core.exceptions import LinKCoveryError

console = Console()


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors gracefully in CLI commands."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except LinKCoveryError as e:
            console.print(f"❌ {e.message}", style="red")
            if e.details:
                console.print(f"   {e.details}", style="dim red")
            raise Exit(1)
        except KeyboardInterrupt:
            console.print("\n🛑 Operation cancelled by user", style="yellow")
            raise Exit(130)
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}", style="red")
            if console._environ.get("LINKCOVERY_DEBUG"):  # type: ignore
                import traceback

                traceback.print_exc()
            raise Exit(1)

    return wrapper


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask for user confirmation."""
    try:
        from rich.prompt import Confirm

        return Confirm.ask(message, default=default)
    except KeyboardInterrupt:
        console.print("\n🛑 Operation cancelled", style="yellow")
        return False
