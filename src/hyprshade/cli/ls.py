from __future__ import annotations

from bisect import bisect_left
from itertools import islice
from typing import final

import click

from hyprshade.shader import Shader

from .utils import ls_dirs


@final
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
    def get_shaders_list(cls) -> list[ShaderWithMeta]:
        current = cls._current()
        shaders = list(map(cls, ls_dirs(Shader.dirs.all())))
        if current:
            i = cls._bisect(shaders, current)
            if shaders[i] == current:
                shaders[i]._is_current = True
                shaders[i]._is_in_shader_paths = True
            else:
                current._is_in_shader_paths = False
                shaders.insert(i, current)
        return shaders

    @classmethod
    def _current(cls) -> ShaderWithMeta | None:
        shader = super().current()
        if shader is None:
            return None
        shader = cls(shader._resolve_path())
        shader._is_current = True
        return shader

    @staticmethod
    def _bisect(a: list[ShaderWithMeta], x: ShaderWithMeta) -> int:
        first_index = bisect_left(a, x.name, key=lambda s: s.name)
        a_prime = islice(a, first_index, None)
        for i, y in enumerate(a_prime, first_index):
            if y.name != x.name:
                break
            if y == x:
                return i
        return first_index


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
