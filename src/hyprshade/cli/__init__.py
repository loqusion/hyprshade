from __future__ import annotations

import logging
from typing import Final

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

COMMANDS: Final = [
    auto,
    current,
    install,
    ls,
    off,
    on,
    toggle,
]


@click.group()
@click.version_option()
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


for command in COMMANDS:
    cli.add_command(command)


def main():
    try:
        return cli()
    except Exception as e:
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            raise e
        message = str(e) or repr(e)
        click.echo(f"{click.style('Error', fg='red')}: {message}", err=True)
        click.secho("Use --verbose to see the full traceback", fg="yellow", err=True)
        return 1
