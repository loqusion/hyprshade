from __future__ import annotations

import shlex

import click

from hyprshade.config.schedule import Schedule

from .utils import get_script_path, write_systemd_user_unit


@click.command(short_help="Install systemd user units")
def install():
    """Install systemd user units.

    Requires a schedule to be specified in hyprshade.toml.
    """

    script_path = get_script_path()
    schedule = Schedule.from_config()
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
