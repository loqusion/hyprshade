from __future__ import annotations

import os
import sys
from os import path
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import click

from hyprshade.config.utils import systemd_user_config_home
from hyprshade.shader import Shader

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T", str, int, float, bool, click.ParamType)
SystemdUnitType = Literal["service", "timer"]


def convert_to_shader(
    ctx: click.Context, param: click.Argument, shader_name_or_path: str | None
) -> Shader | None:
    shader = Shader(shader_name_or_path) if shader_name_or_path is not None else None
    if shader is not None and shader.stale:
        raise click.BadParameter(f"Shader {shader_name_or_path} does not exist")
    return shader


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
    metavar: str | None = None, callback: Callable | None = None
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
