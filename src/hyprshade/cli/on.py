from __future__ import annotations

from typing import TYPE_CHECKING

import click

from .utils import ShaderParamType

if TYPE_CHECKING:
    from hyprshade.shader import Shader


@click.command(short_help="Turn on screen shader")
@click.argument("shader", type=ShaderParamType())
def on(shader: Shader):
    """Turn on screen shader."""

    shader.on()
