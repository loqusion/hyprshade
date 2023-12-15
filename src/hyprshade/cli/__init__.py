from __future__ import annotations

import logging
from typing import Final

import click

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
def cli(verbose: bool):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level)


for command in COMMANDS:
    cli.add_command(command)


def main():
    try:
        return cli()
    except Exception as e:
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            raise e
        click.echo(f"{click.style('Error', fg='red')}: {e!s}", err=True)
        return 1
