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
        self._given_path = (
            shader_name_or_path
            if path.dirname(shader_name_or_path) and path.isfile(shader_name_or_path)
            else None
        )
        self._name = _stripped_basename(shader_name_or_path)

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"Shader({self._name!r})"

    @property
    def name(self) -> str:
        return self._name

    def on(self) -> None:
        path_ = self._resolve_path()
        hyprctl.set_screen_shader(path_)

    @staticmethod
    def off() -> None:
        hyprctl.clear_screen_shader()

    @staticmethod
    def current() -> Shader | None:
        name = hyprctl.get_screen_shader()
        return None if name is None else Shader(name)

    def samefile(self, __value: Shader) -> bool:
        s, s2 = self._resolve_path(), __value._resolve_path()
        return path.samefile(s, s2)

    def _resolve_path(self) -> str:
        if self._given_path:
            return self._given_path

        for dir in SHADER_DIRS:
            path_ = first(iglob(f"{self._name}*", root_dir=dir), None)
            if path_ is not None:
                return path.join(dir, path_)

        raise FileNotFoundError(f"Shader {self._name} does not exist")
