#!/usr/bin/env python

import os
import sys
from os import path

import click
from click.exceptions import Exit
from utils import get_shader_path, get_shaders_dir

EMPTY_STR = "[[EMPTY]]"


@click.command()
def ls() -> int:
    """List available screen shaders"""

    shaders_dir = get_shaders_dir()
    for shader in os.listdir(shaders_dir):
        shader = path.splitext(shader)[0]
        click.echo(shader)
    raise Exit(0)


@click.command()
@click.argument("shader", required=True, type=str)
def on(shader: str) -> int:
    """Turn on screen shader"""

    shader_path = get_shader_path(shader)
    code = os.system(f"hyprctl keyword decoration:screen_shader '{shader_path}'")
    raise Exit(code)


@click.command()
def off() -> int:
    """Turn off screen shader"""

    code = os.system(f"hyprctl keyword decoration:screen_shader '{EMPTY_STR}'")
    raise Exit(code)


@click.group()
def cli():
    pass


COMMANDS = [
    ls,
    off,
    on,
]
for command in COMMANDS:
    cli.add_command(command)


if __name__ == "__main__":
    try:
        sys.exit(cli.main(standalone_mode=False))
    except Exception as err:
        click.echo(err)
        sys.exit(1)
