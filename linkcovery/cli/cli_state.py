"""Global CLI state set by the main callback.

Consoles live in linkcovery.core.utils (one stdout + one stderr pair);
this module only holds runtime flags so any layer can check them.
"""

from dataclasses import dataclass


@dataclass
class CliState:
    """Runtime flags shared across all commands."""

    json_mode: bool = False  # machine-readable output; suppresses spinners/progress
    no_color: bool = False


state = CliState()
