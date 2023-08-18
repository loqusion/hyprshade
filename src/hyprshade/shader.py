from __future__ import annotations

from glob import iglob
from os import path
from typing import Final

from more_itertools import first

from hyprshade.utils import hypr_config_home

from . import hyprctl


def _stripped_basename(s: str) -> str:
    return path.splitext(path.basename(s))[0]


class _ShaderDirs:
    ENV_VAR_NAME: Final = "HYPRSHADE_SHADERS_DIR"

    @staticmethod
    def env() -> str:
        return path.expanduser(
            path.expandvars(path.expandvars("$" + _ShaderDirs.ENV_VAR_NAME))
        )

    SYSTEM_DIR: Final = "/usr/share/hyprshade/shaders"

    @staticmethod
    def system() -> str:
        return _ShaderDirs.SYSTEM_DIR

    @staticmethod
    def user() -> str:
        return path.join(hypr_config_home(), "shaders")

    @staticmethod
    def all() -> list[str]:
        return [
            x
            for x in [_ShaderDirs.env(), _ShaderDirs.system(), _ShaderDirs.user()]
            if path.exists(x)
        ]


class Shader:
    dirs: Final = _ShaderDirs

    def __init__(self, shader_name_or_path: str):
        self._given_path = (
            shader_name_or_path
            if path.dirname(shader_name_or_path) and path.isfile(shader_name_or_path)
            else None
        )
        self._name = _stripped_basename(shader_name_or_path)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Shader):
            return False
        s, s2 = self._resolve_path(), __value._resolve_path()
        return path.samefile(s, s2)

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

    def _resolve_path(self) -> str:
        if self._given_path:
            return self._given_path

        dirs = Shader.dirs.all()
        for dir in dirs:
            path_ = first(iglob(f"{self._name}*", root_dir=dir), None)
            if path_ is not None:
                return path.join(dir, path_)

        raise FileNotFoundError(
            f"Shader '{self._name}' could not be found in any of the following"
            " directories:\n\t"
            "{}".format("\n\t".join(dirs))
        )
