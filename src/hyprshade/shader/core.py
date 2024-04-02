from __future__ import annotations

from datetime import datetime, timedelta
import logging
import os
from typing import TYPE_CHECKING, Final

from more_itertools import flatten

from hyprshade.template import mustache
from hyprshade.template.constants import TEMPLATE_EXTENSIONS
from hyprshade.utils.fs import scandir_recursive
from hyprshade.utils.path import strip_all_extensions, stripped_basename
from hyprshade.utils.xdg import user_state_dir

from . import hyprctl
from .dirs import ShaderDirs

if TYPE_CHECKING:
    from hyprshade.config.core import Config


class PureShader:
    _name: str
    _given_path: str | None

    def __init__(self, shader_name_or_path: str):
        if shader_name_or_path.find(os.path.sep) != -1:
            self._name = PureShader.path_to_name(shader_name_or_path)
            self._given_path = os.path.abspath(shader_name_or_path)
        else:
            if shader_name_or_path.find(".") != -1:
                raise ValueError(
                    f"Shader name '{shader_name_or_path}' must not contain a '.' character"
                )
            self._name = shader_name_or_path
            self._given_path = None

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, PureShader):
            return False
        try:
            s1, s2 = self._resolve_path(), __value._resolve_path()
        except FileNotFoundError:
            return False
        return os.path.samefile(s1, s2)

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._name!r})"

    @property
    def name(self) -> str:
        return self._name

    def path(self) -> str:
        return self._resolve_path()

    def dirname(self) -> str:
        return os.path.dirname(self._resolve_path())

    @staticmethod
    def path_to_name(path: str) -> str:
        return stripped_basename(path)

    def _resolve_path(self) -> str:
        if self._given_path:
            if not os.path.exists(self._given_path):
                raise FileNotFoundError(f"No file found at '{self._given_path}'")
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


class Shader(PureShader):
    dirs: Final = ShaderDirs
    _config: Config | None

    def __init__(self, shader_name_or_path: str, config: Config | None):
        super().__init__(shader_name_or_path)
        self._config = config

    def on(self) -> None:
        path = self._resolve_path_after_intermediate_steps()
        logging.debug(f"Turning on shader '{self._name}' at '{path}'")
        hyprctl.set_screen_shader(path)

    @staticmethod
    def off() -> None:
        hyprctl.clear_screen_shader()

    @staticmethod
    def current() -> PureShader | None:
        path = hyprctl.get_screen_shader()
        return None if path is None else PureShader(path)

    def _resolve_path_after_intermediate_steps(self) -> str:
        path = self._resolve_path()
        _, extension = os.path.splitext(os.path.basename(path))
        if extension.strip(".") in TEMPLATE_EXTENSIONS:
            return self._render_template(path)
        return path

    def _render_template(self, path: str) -> str:
        with open(path) as f:
            variables = (
                self._config.shader_variables(self._name) if self._config else None
            )

            config = self._config.shader_config(self._name) if self._config else None
            if config is not None and config.gradual_shift_times is not None and config.start_time is not None:
                now = datetime.now().time()
                now_delta = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
                start_delta = timedelta(hours=config.start_time.hour,minutes=config.start_time.minute,seconds=config.start_time.second)

                delta = now_delta - start_delta

                percentage_increase=1.0/(len(config.gradual_shift_times)+1)
                percentage = percentage_increase
                for i in range(0, len(config.gradual_shift_times)):
                    if delta < config.gradual_shift_times[i]:
                        break
                    percentage = percentage + percentage_increase
                percentage = round(percentage, 2) # round to get clearer values in the shader

                if variables is None:
                    variables = {"gradualPercentage": percentage}
                else:
                    variables["gradualPercentage"] = percentage
                pass
            content = mustache.render(f, variables)
        base, _ = os.path.splitext(os.path.basename(path))
        rendered_path = os.path.join(user_state_dir("hyprshade"), base)
        os.makedirs(os.path.dirname(rendered_path), exist_ok=True)
        with open(rendered_path, "w") as f:
            f.write(content)
        return rendered_path
