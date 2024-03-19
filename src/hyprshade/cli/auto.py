from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import click

from hyprshade.config.schedule import Schedule
from hyprshade.shader.core import Shader

if TYPE_CHECKING:
    from hyprshade.cli.utils import ContextObject


@click.command(short_help="Set screen shader on schedule")
@click.pass_obj
def auto(obj: ContextObject):
    """Set screen shader based on schedule.

    Requires a schedule to be specified in hyprshade.toml.
    """

    t = datetime.now().time()
    config = obj.get_config(raising=True)
    shader = Schedule(config).scheduled_shader(t)

    if shader:
        shader.on()
    else:
        Shader.off()
