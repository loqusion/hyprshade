from __future__ import annotations

from bisect import bisect

import click

from hyprshade.shader import Shader

from .utils import ls_dirs


@click.command(short_help="List available screen shaders")
@click.option("-l", "--long", is_flag=True, help="Long listing format")
def ls(long: bool):
    """List available screen shaders."""

    current = Shader.current()
    shaders = list(map(Shader, ls_dirs(Shader.dirs.all())))
    current_in_shader_paths = False
    if current:
        current_in_shader_paths = True
        b = bisect(shaders, current.name, key=lambda s: s.name)
        if b == 0 or shaders[b - 1] != current:
            current_in_shader_paths = False
            shaders.insert(b, current)
    if not shaders:
        return
    width = max(map(len, map(str, shaders))) + 1

    for shader in shaders:
        is_shader_current = shader == current
        c = "*" if is_shader_current else " "
        if long:
            dir = shader.dirname()
            click.echo(f"{c} {shader!s:{width}} {dir}")
            continue
        if is_shader_current and not current_in_shader_paths:
            click.echo(f"{c} {shader!s}  ({shader.dirname()})")
            continue
        click.echo(f"{c} {shader!s}")
