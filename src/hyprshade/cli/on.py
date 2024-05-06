from __future__ import annotations

from typing import TYPE_CHECKING

import click

from .utils import (
    MergedVarOption,
    ShaderParamType,
    variables_option,
)

if TYPE_CHECKING:
    from hyprshade.shader.core import Shader


@click.command(short_help="Turn on screen shader")
@click.argument("shader", type=ShaderParamType())
@variables_option()
def on(shader: Shader, variables: MergedVarOption):
    """Turn on screen shader."""

    shader.on(variables)
