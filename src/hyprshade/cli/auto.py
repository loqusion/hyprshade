from __future__ import annotations

from datetime import datetime

import click

from hyprshade.config.schedule import Schedule
from hyprshade.shader import Shader


@click.command(short_help="Set screen shader on schedule")
@click.pass_context
def auto(ctx: click.Context):
    """Set screen shader based on schedule.

    Requires a schedule to be specified in hyprshade.toml.
    """

    t = datetime.now().time()
    shader = Schedule.from_config().scheduled_shader(t)

    if shader:
        shader.on()
    else:
        Shader.off()
