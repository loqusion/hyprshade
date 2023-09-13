from __future__ import annotations

import click

from hyprshade.shader import Shader


@click.command(short_help="Turn off screen shader")
def off():
    """Turn off screen shader."""

    Shader.off()
