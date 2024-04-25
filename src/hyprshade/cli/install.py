from __future__ import annotations

import os
import shlex
from typing import Literal, TypeAlias

import click

from hyprshade.config.schedule import Schedule
from hyprshade.utils.xdg import user_config_dir

from .utils import ContextObject, get_script_path


@click.command(short_help="Install systemd user units")
@click.pass_obj
def install(obj: ContextObject):
    """Install systemd user units.

    Requires a schedule to be specified in hyprshade.toml.
    """

    script_path = get_script_path()
    config = obj.get_config(raising=True)
    schedule = Schedule(config)
    timer_config = "\n".join(
        sorted([f"OnCalendar=*-*-* {x}" for x in schedule.event_times()])
    )

    write_systemd_user_unit(
        "service",
        f"""[Unit]
Description=Apply screen filter

[Service]
Type=oneshot
ExecStart={shlex.quote(script_path)} auto
""",
    )

    write_systemd_user_unit(
        "timer",
        f"""[Unit]
Description=Apply screen filter on schedule

[Timer]
{timer_config}

[Install]
WantedBy=timers.target
""",
    )


SystemdUnitType: TypeAlias = Literal["service", "timer"]


def write_systemd_user_unit(unit_type: SystemdUnitType, body: str) -> None:
    dest_dir = user_config_dir("systemd/user")
    os.makedirs(dest_dir, exist_ok=True)
    with open(os.path.join(dest_dir, f"hyprshade.{unit_type}"), "w") as f:
        f.write(body)
