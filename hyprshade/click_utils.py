from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import click

from .shader import Shader

if TYPE_CHECKING:
    from collections.abc import Callable


def convert_to_shader(
    ctx: click.Context, param: click.Argument, shader_name_or_path: str | None
):
    return Shader(shader_name_or_path) if shader_name_or_path is not None else None


T = TypeVar("T", str, int, float, bool, click.ParamType)


def validate_optional_param(
    ctx: click.Context, param: click.Argument, value: tuple[T, ...]
) -> T | None:
    if extra_args := value[1:]:
        s = "s" if len(extra_args) > 1 else ""
        raise click.UsageError(
            f"Got unexpected extra argument{s} ({' '.join(map(str, extra_args))})"
        )

    return None if len(value) == 0 else value[0]


def optional_param(metavar: str | None = None, callback: Callable | None = None):
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
