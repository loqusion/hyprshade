from __future__ import annotations

import click

from hyprshade.shader import Shader


@click.command(short_help="Print current screen shader")
def current():
    """Print current screen shader."""

    print(Shader.current())
