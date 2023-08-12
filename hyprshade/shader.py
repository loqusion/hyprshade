from __future__ import annotations

from glob import iglob
from os import path

from more_itertools import first

from . import hyprctl
from .constants import SHADER_DIRS


def _stripped_basename(s: str) -> str:
    return path.splitext(path.basename(s))[0]


class Shader:
    def __init__(self, shader_name_or_path: str):
        self._shader_path = (
            shader_name_or_path if path.isfile(shader_name_or_path) else None
        )
        self._shader_name = _stripped_basename(shader_name_or_path)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Shader):
            return False
        s, s2 = self._resolve_path(), __value._resolve_path()
        return path.samefile(s, s2)

    def __str__(self) -> str:
        return self._shader_name

    def __repr__(self) -> str:
        return f"Shader({self._shader_name!r})"

    @property
    def shader_name(self) -> str:
        return self._shader_name

    def on(self) -> None:
        shader_path = self._resolve_path()
        hyprctl.set_screen_shader(shader_path)

    @staticmethod
    def off() -> None:
        hyprctl.clear_screen_shader()

    @staticmethod
    def current() -> Shader | None:
        shader_name = hyprctl.get_screen_shader()
        return None if shader_name is None else Shader(shader_name)

    def _resolve_path(self) -> str:
        if self._shader_path:
            return self._shader_path

        for dir in SHADER_DIRS:
            shader_path = first(iglob(f"{self._shader_name}*", root_dir=dir), None)
            if shader_path is not None:
                return path.join(dir, shader_path)

        raise FileNotFoundError(f"Shader {self._shader_name} does not exist")
