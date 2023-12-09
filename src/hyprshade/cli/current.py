from __future__ import annotations

import click

from hyprshade.shader import Shader


@click.command(short_help="Print current screen shader")
def current():
    """Print current screen shader.

    If no shader is active, print nothing.
    """

    current = Shader.current()
    if current is None:
        return
    print(current)
