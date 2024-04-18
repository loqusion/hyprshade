from __future__ import annotations

import logging
import os
from collections.abc import Callable
from functools import cached_property
from typing import Any, Final, TypeVar, Union

from more_itertools import flatten

from hyprshade.template import mustache
from hyprshade.template.constants import TEMPLATE_EXTENSIONS
from hyprshade.utils.fs import scandir_recursive
from hyprshade.utils.path import strip_all_extensions, stripped_basename
from hyprshade.utils.xdg import user_state_dir

from . import hyprctl
from .dirs import ShaderDirs

T = TypeVar("T")
PossiblyLazy = Union[T, Callable[[], T]]  # noqa: UP007

ShaderVariables = dict[str, Any]


class PureShader:
    _name: str
    _given_path: str | None
    _template_instance_path: str | None

    def __init__(
        self, shader_name_or_path: str, *, template_instance_path: str | None = None
    ):
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
        self._template_instance_path = template_instance_path

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

    @property
    def template_instance_path(self) -> str | None:
        return self._template_instance_path

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
    _variables: PossiblyLazy[ShaderVariables | None]

    TEMPLATE_METADATA_PREFIX: Final = "// SOURCE:"

    def __init__(
        self,
        shader_name_or_path: str,
        variables: PossiblyLazy[ShaderVariables | None],
        template_instance_path: str | None = None,
    ):
        super().__init__(
            shader_name_or_path, template_instance_path=template_instance_path
        )
        self._variables = variables

    def on(self) -> None:
        source_path = self._resolve_path()
        _, source_path_extension = os.path.splitext(os.path.basename(source_path))
        if source_path_extension.strip(".") in TEMPLATE_EXTENSIONS:
            rendered_path = self._render_template(source_path)
        else:
            rendered_path = source_path
        logging.debug(f"Turning on shader '{self._name}' at '{rendered_path}'")
        hyprctl.set_screen_shader(rendered_path)

    @staticmethod
    def off() -> None:
        hyprctl.clear_screen_shader()

    @staticmethod
    def current() -> PureShader | None:
        path = hyprctl.get_screen_shader()
        if path is not None and (
            os.path.commonpath([path, user_state_dir("hyprshade")])
            == user_state_dir("hyprshade")
        ):
            return PureShader(
                Shader._extract_source_path_from_template(path),
                template_instance_path=path,
            )
        return None if path is None else PureShader(path)

    @cached_property
    def variables(self) -> ShaderVariables | None:
        if callable(self._variables):
            return self._variables()
        return self._variables

    def _render_template(self, path: str) -> str:
        with open(path) as f:
            content = mustache.render(f, self.variables)
        out_path = Shader._template_path_from_source_path(path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            f.write(f"{Shader.TEMPLATE_METADATA_PREFIX} {path}\n")
            f.write(content)
        return out_path

    @staticmethod
    def _template_path_from_source_path(path: str) -> str:
        file_name, _ = os.path.splitext(os.path.basename(path))
        return os.path.join(user_state_dir("hyprshade"), file_name)

    @staticmethod
    def _extract_source_path_from_template(path: str) -> str:
        with open(path) as f:
            first_line = f.readline()
            if not first_line.startswith(Shader.TEMPLATE_METADATA_PREFIX):
                raise ValueError(
                    f"Expected first line of file '{path}' to start with '{Shader.TEMPLATE_METADATA_PREFIX}'"
                )
            source_path = first_line.removeprefix(
                Shader.TEMPLATE_METADATA_PREFIX
            ).strip()
            return source_path
