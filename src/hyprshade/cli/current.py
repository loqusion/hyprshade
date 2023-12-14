from __future__ import annotations

import click

from hyprshade.shader import Shader


@click.command(short_help="Print current screen shader")
@click.option("-l", "--long", is_flag=True, help="Long listing format")
def current(long: bool):
    """Print current screen shader.

    If no shader is active, print nothing.
    """

    current = Shader.current()
    if current is None:
        return

    if long:
        click.echo(f"{current}  {current.dirname()}")
        return
    click.echo(current)
