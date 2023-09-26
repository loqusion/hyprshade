from __future__ import annotations

import click

from hyprshade.config.schedule import Schedule

from .utils import write_systemd_user_unit


@click.command(short_help="Install systemd user units")
def install():
    """Install systemd user units."""

    schedule = Schedule.from_config()
    timer_config = "\n".join(
        sorted([f"OnCalendar=*-*-* {x}" for x in schedule.event_times()])
    )

    write_systemd_user_unit(
        "service",
        """[Unit]
Description=Apply screen filter

[Service]
Type=oneshot
ExecStart="/usr/bin/hyprshade" auto
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
