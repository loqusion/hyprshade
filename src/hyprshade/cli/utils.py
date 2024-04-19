from __future__ import annotations

import os
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Literal,
    NamedTuple,
    TypeAlias,
    TypeVar,
    overload,
)

import click
from more_itertools import unique_justseen

from hyprshade.config.core import Config
from hyprshade.shader.core import Shader
from hyprshade.utils.fs import ls_dirs
from hyprshade.utils.path import stripped_basename

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

    from click.decorators import FC


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


def optional_argument(
    *param_decls: str,
    cls: type[click.Argument] | None = None,
    metavar: str,
    **attrs: Any,
) -> Callable[[FC], FC]:
    def merged_callback(
        ctx: click.Context, param: click.Argument, value: tuple[T, ...]
    ):
        optional_value = validate_optional_param(ctx, param, value)
        if (callback := attrs.get("callback")) is not None:  # pragma: no cover
            return callback(ctx, param, optional_value)
        return optional_value

    return click.argument(
        *param_decls,
        cls=cls,
        metavar=metavar,
        **attrs,
        nargs=-1,
        callback=merged_callback,
    )


class ShaderParamType(click.ParamType):
    name: Final = "shader"

    def convert(
        self,
        value: str,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ):
        obj: ContextObject | None = ctx.obj if ctx is not None else None
        config = obj.get_config() if obj is not None else None
        lazy_variables = (
            config.lazy_shader_variables(value) if config is not None else None
        )
        shader_conf = config.shader_config(value) if config is not None else None
        gradual_shift_duration = 0
        if shader_conf is not None:
            gradual_shift_duration = shader_conf.gradual_shift_duration if shader_conf.gradual_shift_duration is not None else 0
        return Shader(value, lazy_variables, gradual_shift_duration)

    def shell_complete(
        self, ctx: click.Context, param: click.Parameter, incomplete: str
    ):
        from click.shell_completion import CompletionItem

        is_path = incomplete.find(os.path.sep) != -1
        if is_path:
            return click.Path().shell_complete(ctx, param, incomplete)

        return [CompletionItem(name) for name in ShaderParamType._shader_names()]

    @staticmethod
    def _shader_names() -> Iterator[str]:
        return unique_justseen(
            sorted(map(stripped_basename, ls_dirs(Shader.dirs.all())))
        )


def dict_set_deep(d: dict[str, Any], keys: list[str], value: Any):
    for key in keys[:-1]:
        if not isinstance(d.get(key), dict):
            d[key] = {}
        d = d[key]
    d[keys[-1]] = value


MergedVarOption: TypeAlias = dict[str, Any]
VarValue: TypeAlias = int | float | str


class VarOptionPair(NamedTuple):
    key: str
    value: VarValue

    @staticmethod
    def merge(pairs: Iterable[VarOptionPair]) -> MergedVarOption:
        merged: MergedVarOption = {}
        for key, value in pairs:
            keys = key.split(".")
            dict_set_deep(merged, keys, value)

        return merged

    @staticmethod
    def convert_value(value: str) -> VarValue:
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value


class VarParamType(click.ParamType):
    name: Final = "var"

    def convert(
        self,
        value: str,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> VarOptionPair:
        try:
            key, value_ = value.split("=", 1)
        except ValueError as e:
            raise click.BadParameter("Must be in the form 'key=value'") from e
        return VarOptionPair(key, VarOptionPair.convert_value(value_))


def variables_option(
    *param_decls: str, cls: type[click.Option] | None = None, **attrs: Any
) -> Callable[[FC], FC]:
    def __to_dict_callback(
        ctx: click.Context,
        param: click.Parameter,
        value: tuple[VarOptionPair, ...],
    ) -> MergedVarOption:
        merged = VarOptionPair.merge(value)
        if (callback := attrs.get("callback")) is not None:  # pragma: no cover
            return callback(ctx, param, merged)
        return merged

    if len(param_decls) == 0:
        param_decls = ("--var", "variables")

    return click.option(
        *param_decls,
        cls=cls,
        metavar="KEY=VALUE",
        help="Variables to pass to the shader. May be specified multiple times.",
        **attrs,
        type=VarParamType(),
        multiple=True,
        callback=__to_dict_callback,
    )


class ContextObject:
    _config: Config | None

    def __init__(self, config: Config | None):
        self._config = config

    @overload
    def get_config(self, raising: Literal[True]) -> Config: ...
    @overload
    def get_config(self, raising: bool = False) -> Config | None: ...
    def get_config(self, raising: bool = False) -> Config | None:
        if self._config is None and raising:
            Config.raise_not_found()
        return self._config
