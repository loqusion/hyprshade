from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

import click

from hyprshade.cli.utils import ContextObject
from hyprshade.config.core import Config

from .auto import auto
from .current import current
from .install import install
from .ls import ls
from .off import off
from .on import on
from .toggle import toggle

if TYPE_CHECKING:
    from collections.abc import Callable


COMMANDS: Final = [
    auto,
    current,
    install,
    ls,
    off,
    on,
    toggle,
]
COMMON_DECORATORS: Final = [
    click.help_option(help="Show this message and exit"),
]


@click.group()
@click.version_option(help="Show the version and exit")
@click.help_option(help="Show this message and exit")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level)

    try:
        config = Config()
    except FileNotFoundError:
        config = None
    ctx.obj = ContextObject(config)


def compose(*decorators: Callable):
    def decorator(f):
        for d in decorators:
            f = d(f)
        return f

    return decorator


for command in COMMANDS:
    cli.add_command(compose(*COMMON_DECORATORS)(command))


def main():  # pragma: no cover
    try:
        return cli()
    except Exception as e:
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            raise e
        message = str(e) or repr(e)
        click.echo(f"{click.style('Error', fg='red')}: {message}", err=True)
        if e.__notes__:
            for note in e.__notes__:
                click.echo(f"{click.style('Note', bold=True)}: {note}", err=True)
        click.secho("Use --verbose to see the full traceback", fg="yellow", err=True)
        return 1
