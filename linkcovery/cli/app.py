"""The cfui App plus the `command` decorator every CLI module registers with."""

import inspect
import os

from cfui import App, Arg

from linkcovery import __version__
from linkcovery.cli.cli_state import state

app = App(
    "linkcovery",
    repo="https://github.com/arian24b/linkcovery",
    version=__version__,
    pypi="linkcovery",
    description="Bookmark and link management: add, search, organize, import/export and a web UI.",
    global_args=[
        Arg("--json", dest="json_mode", action="store_true", help="Output machine-readable JSON"),
        Arg("--no-color", action="store_true", help="Disable colored output"),
    ],
)


def command(parent, name, help_, args=(), aliases=(), **kw):
    """Register `fn(**options)`; options are taken from the parsed namespace by parameter name."""

    def deco(fn):
        params = list(inspect.signature(fn).parameters)

        def runner(a):
            state.json_mode, state.no_color = a.json_mode, a.no_color
            if a.no_color:
                os.environ["NO_COLOR"] = "1"
            return fn(**{k: getattr(a, k) for k in params})

        parent.command(name, help_, args=args, aliases=aliases, **kw)(runner)
        return fn

    return deco
