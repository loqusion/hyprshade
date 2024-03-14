from __future__ import annotations

import os
import sys
from os import path
from typing import TYPE_CHECKING, Any, Final, Literal, TypeVar

import click
from more_itertools import flatten, unique_justseen

from hyprshade.config.utils import systemd_user_config_home
from hyprshade.shader import Shader
from hyprshade.utils import scandir_recursive, stripped_basename

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from os import PathLike

T = TypeVar("T", str, int, float, bool, click.ParamType)
SystemdUnitType = Literal["service", "timer"]


def validate_optional_param(
    ctx: click.Context, param: click.Argument, value: tuple[T, ...]
) -> T | None:
    if extra_args := value[1:]:
        s = "s" if len(extra_args) > 1 else ""
        raise click.UsageError(
            f"Got unexpected extra argument{s} ({' '.join(map(str, extra_args))})"
        )

    return None if len(value) == 0 else value[0]


def optional_param(
    metavar: str | None = None, *, callback: Callable | None = None
) -> dict[str, Any]:
    def merged_callback(
        ctx: click.Context, param: click.Argument, value: tuple[T, ...]
    ):
        value2 = validate_optional_param(ctx, param, value)
        if callback is not None:
            return callback(ctx, param, value2)
        return value2

    return {
        "metavar": metavar,
        "nargs": -1,
        "callback": merged_callback,
    }


def write_systemd_user_unit(unit_type: SystemdUnitType, body: str) -> None:
    dest_dir = systemd_user_config_home()
    os.makedirs(dest_dir, exist_ok=True)
    with open(path.join(dest_dir, f"hyprshade.{unit_type}"), "w") as f:
        f.write(body)


def get_script_path() -> str:
    return path.realpath(sys.argv[0], strict=True)


def ls_dirs(dirs: Iterable[str | PathLike[str]]) -> Iterator[str]:
    all_files = flatten(scandir_recursive(d, max_depth=5) for d in dirs)
    return (f.path for f in sorted(all_files, key=lambda f: f.name))


class ShaderParamType(click.ParamType):
    name: Final = "shader"

    def convert(
        self,
        value: str,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ):
        return Shader(value)

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ):
        from click.shell_completion import CompletionItem

        is_path = incomplete.find(path.sep) != -1
        if is_path:
            return click.Path().shell_complete(ctx, param, incomplete)

        return [CompletionItem(name) for name in ShaderParamType._shader_names()]

    @staticmethod
    def _shader_names() -> Iterable[str]:
        return unique_justseen(
            sorted(map(stripped_basename, ls_dirs(Shader.dirs.all())))
        )
