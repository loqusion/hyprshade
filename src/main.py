#!/usr/bin/env python

import os
import sys
from os import path

import click
from utils import get_shader_path, get_shaders_dir

EMPTY_STR = "[[EMPTY]]"


@click.command()
def ls() -> int:
    """List available screen shaders"""

    shaders_dir = get_shaders_dir()
    for shader in os.listdir(shaders_dir):
        shader = path.splitext(shader)[0]
        click.echo(shader)
    return 0


@click.command()
@click.argument("shader", required=True, type=str)
def on(shader: str) -> int:
    """Turn on screen shader"""

    shader_path = get_shader_path(shader)
    code = os.system(f"hyprctl keyword decoration:screen_shader '{shader_path}'")
    return code


@click.command()
def off() -> int:
    """Turn off screen shader"""

    code = os.system(f"hyprctl keyword decoration:screen_shader '{EMPTY_STR}'")
    return code


@click.command()
@click.argument("shader", required=True, type=str)
@click.pass_context
def toggle(ctx: click.Context, shader: str) -> int:
    """Toggle screen shader"""

    import json
    from json import JSONDecodeError

    current_shader: str | None = None
    try:
        o = json.load(os.popen("hyprctl -j getoption decoration:screen_shader"))
        current_shader = str(o["str"]).strip()
    except JSONDecodeError:
        click.echo("Failed to get current screen shader", err=True)
        return 1

    if path.isfile(current_shader) and path.samefile(
        get_shader_path(shader), current_shader
    ):
        ctx.invoke(off)
        return 0

    return ctx.invoke(on, shader=shader)


@click.command()
def auto() -> int:
    from config import Config

    c = Config("examples/config.toml")
    for shade in c.shades:
        print(shade)

    return 0


@click.group()
def cli():
    pass


COMMANDS = [
    auto,
    ls,
    off,
    on,
    toggle,
]
for command in COMMANDS:
    cli.add_command(command)


if __name__ == "__main__":
    try:
        sys.exit(cli.main(standalone_mode=False))
    except Exception as err:
        click.echo(err, err=True)
        sys.exit(1)
