from __future__ import annotations

import os
import shlex
import subprocess
import sys
from typing import TYPE_CHECKING, Literal, TypeAlias

import click

from hyprshade.config.schedule import Schedule
from hyprshade.utils.xdg import user_config_dir

if TYPE_CHECKING:
    from .utils import ContextObject


@click.command(short_help="Install systemd user units")
@click.option("--enable", is_flag=True, help="Enable the units after installation")
@click.pass_obj
def install(obj: ContextObject, enable: bool):
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

    if enable:
        subprocess.run(
            ["systemctl", "--user", "enable", "--now", "hyprshade.timer"],
            check=True,
        )


SystemdUnitType: TypeAlias = Literal["service", "timer"]


def get_script_path() -> str:  # pragma: no cover
    return os.path.realpath(sys.argv[0], strict=True)


def write_systemd_user_unit(unit_type: SystemdUnitType, text: str) -> None:
    dest_dir = user_config_dir("systemd/user")
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, f"hyprshade.{unit_type}")
    with open(path, "w") as f:
        f.write(text)
    click.echo(f"Wrote {unit_type} unit to {path}.", err=True)
