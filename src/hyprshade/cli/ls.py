from __future__ import annotations

from bisect import bisect

import click

from hyprshade.shader import Shader

from .utils import ls_dirs


class ShaderWithMeta(Shader):
    _is_current: bool
    _is_in_shader_paths: bool | None

    def __init__(self, shader_name_or_path: str):
        super().__init__(shader_name_or_path)
        self._is_current = False
        self._is_in_shader_paths = None

    @property
    def is_current(self):
        return self._is_current

    @property
    def is_in_shader_paths(self):
        is_in_shader_paths = self._is_in_shader_paths
        if is_in_shader_paths is None:
            raise RuntimeError("ShaderWithMeta.is_in_shader_paths is not set")
        return is_in_shader_paths

    @classmethod
    def _current(cls) -> ShaderWithMeta | None:
        shader = super().current()
        if shader is None:
            return None
        shader = cls(shader._resolve_path())
        shader._is_current = True
        return shader

    @staticmethod
    def get_shaders_list() -> list[ShaderWithMeta]:
        current = ShaderWithMeta._current()
        shaders = list(map(ShaderWithMeta, ls_dirs(Shader.dirs.all())))
        if current:
            i = bisect(shaders, current.name, key=lambda s: s.name)
            is_current_in_shaders = i != 0 and shaders[i - 1] == current
            if is_current_in_shaders:
                shaders[i - 1]._is_current = True
                shaders[i - 1]._is_in_shader_paths = True
            else:
                current._is_in_shader_paths = False
                shaders.insert(i, current)
        return shaders


@click.command(short_help="List available screen shaders")
@click.option("-l", "--long", is_flag=True, help="Long listing format")
def ls(long: bool):
    """List available screen shaders."""

    shaders = ShaderWithMeta.get_shaders_list()
    if not shaders:
        return
    width = max(map(len, map(str, shaders))) + 1

    for shader in shaders:
        c = "*" if shader.is_current else " "
        if long:
            click.echo(f"{c} {shader!s:{width}} {shader.dirname()}")
            continue
        if shader.is_current and not shader.is_in_shader_paths:
            click.echo(f"{c} {shader!s}  ({shader.dirname()})")
            continue
        click.echo(f"{c} {shader!s}")
