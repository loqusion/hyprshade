from __future__ import annotations

from typing import TYPE_CHECKING

import click

from .utils import ShaderParamType, option_variables

if TYPE_CHECKING:
    from hyprshade.shader.core import Shader


@click.command(short_help="Turn on screen shader")
@click.argument("shader", type=ShaderParamType())
@click.option(
    "--var",
    "-V",
    "variables",
    **option_variables(),
)
def on(shader: Shader, variables: dict[str, str]):
    """Turn on screen shader."""

    shader.on(variables)
