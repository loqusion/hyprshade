from __future__ import annotations

import logging
import os
from functools import cached_property
from typing import Final

from more_itertools import first_true, flatten

from hyprshade.config.utils import hypr_config_home, hyprshade_config_home
from hyprshade.utils.fs import scandir_recursive
from hyprshade.utils.path import strip_all_extensions, stripped_basename

from . import hyprctl


class _ShaderDirs:
    ENV_VAR_NAME: Final = "HYPRSHADE_SHADERS_DIR"
    SYSTEM_DIR: Final = "/usr/share/hyprshade/shaders"

    @staticmethod
    def env() -> str:
        return os.path.expanduser(
            os.path.expandvars(os.path.expandvars("$" + _ShaderDirs.ENV_VAR_NAME))
        )

    @staticmethod
    def user_hypr() -> str:
        return os.path.join(hypr_config_home(), "shaders")

    @staticmethod
    def user_hyprshade() -> str:
        return os.path.join(hyprshade_config_home(), "shaders")

    @staticmethod
    def system() -> str:
        import sysconfig

        return first_true(
            [os.path.join(sysconfig.get_path("data"), "share", "hyprshade", "shaders")],
            pred=os.path.exists,
            default=_ShaderDirs.SYSTEM_DIR,
        )

    @staticmethod
    def all() -> list[str]:
        return [
            x
            for x in [
                _ShaderDirs.env(),
                _ShaderDirs.user_hypr(),
                _ShaderDirs.user_hyprshade(),
                _ShaderDirs.system(),
            ]
            if os.path.exists(x)
        ]


class Shader:
    dirs: Final = _ShaderDirs
    _given_path: str | None
    _name: str

    def __init__(self, shader_name_or_path: str):
        if shader_name_or_path.find(os.path.sep) != -1:
            self._given_path = os.path.abspath(shader_name_or_path)
            self._name = stripped_basename(self._given_path)
        elif shader_name_or_path.find(".") != -1:
            raise ValueError(
                f"Shader name '{shader_name_or_path}' must not contain a '.' character"
            )
        else:
            self._given_path = None
            self._name = shader_name_or_path

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Shader):
            return False
        try:
            s1, s2 = self._resolve_path(), __value._resolve_path()
        except FileNotFoundError:
            return False
        return os.path.samefile(s1, s2)

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"Shader({self._name!r})"

    @property
    def name(self) -> str:
        return self._name

    @cached_property
    def does_given_path_exist(self) -> bool:
        return self._given_path is None or os.path.exists(self._given_path)

    def dirname(self) -> str:
        return os.path.dirname(self._resolve_path())

    def on(self) -> None:
        path = self._resolve_path()
        logging.debug(f"Turning on shader '{self._name}' at '{path}'")
        hyprctl.set_screen_shader(path)

    @staticmethod
    def off() -> None:
        hyprctl.clear_screen_shader()

    @staticmethod
    def current() -> Shader | None:
        path = hyprctl.get_screen_shader()
        return None if path is None else Shader(path)

    def _resolve_path(self) -> str:
        if not self.does_given_path_exist:
            raise FileNotFoundError(f"No file found at '{self._given_path}'")
        if self._given_path:
            return self._given_path
        return self._resolve_path_from_shader_dirs()

    def _resolve_path_from_shader_dirs(self) -> str:
        dirs = Shader.dirs.all()
        all_files = flatten(scandir_recursive(d, max_depth=5) for d in dirs)
        for file in all_files:
            if strip_all_extensions(file.name) == self._name:
                return file.path

        raise FileNotFoundError(
            f"Shader '{self._name}' could not be found in any of the following"
            " directories:\n\t"
            "{}".format("\n\t".join(dirs))
        )
