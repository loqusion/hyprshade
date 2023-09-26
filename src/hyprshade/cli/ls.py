from __future__ import annotations

import click

from hyprshade.shader import Shader

from .utils import ls_dirs


@click.command(short_help="List available screen shaders")
@click.option("-l", "--long", is_flag=True, help="Long listing format")
def ls(long: bool):
    """List available screen shaders."""

    current = Shader.current()
    shaders = list(map(Shader, ls_dirs(Shader.dirs.all())))
    if not shaders:
        return
    width = max(map(len, map(str, shaders))) + 1

    for shader in shaders:
        c = "*" if shader == current else " "
        if long:
            dir = shader.dirname()
            click.echo(f"{c} {shader!s:{width}} {dir}")
            continue
        click.echo(f"{c} {shader!s}")
