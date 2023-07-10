import os
import sys
from datetime import datetime
from os import path
from typing import Final

import typer

from hyprshade.helpers import get_shader_path, get_shaders_dir
from hyprshade.utils import systemd_user_config_home

EMPTY_STR: Final = "[[EMPTY]]"

app = typer.Typer()


@app.command()
def ls() -> int:
    """List available screen shaders"""

    shaders_dir = get_shaders_dir()
    for shader in os.listdir(shaders_dir):
        shader = path.splitext(shader)[0]
        print(shader)
    return 0


@app.command()
def on(shader: str) -> int:
    """Turn on screen shader"""

    shader_path = get_shader_path(shader)
    code = os.system(f"hyprctl keyword decoration:screen_shader '{shader_path}'")
    return code


@app.command()
def off() -> int:
    """Turn off screen shader"""

    code = os.system(f"hyprctl keyword decoration:screen_shader '{EMPTY_STR}'")
    return code


@app.command()
def toggle(shader: str) -> int:
    """Toggle screen shader"""

    import json
    from json import JSONDecodeError

    current_shader: str | None = None
    try:
        o = json.load(os.popen("hyprctl -j getoption decoration:screen_shader"))
        current_shader = str(o["str"]).strip()
    except JSONDecodeError:
        print("Failed to get current screen shader", file=sys.stderr)
        return 1

    if path.isfile(current_shader) and path.samefile(
        get_shader_path(shader), current_shader
    ):
        off()
        return 0

    return on(shader)


@app.command()
def auto() -> int:
    from hyprshade.config import Config

    t = datetime.now().time()
    schedule = Config().to_schedule()
    shade = schedule.contained(t)
    if shade is not None:
        return on(shade)

    return off()


@app.command()
def install() -> int:
    from hyprshade.config import Config

    schedule = Config().to_schedule()

    with open(path.join(systemd_user_config_home(), "hyprshade.service"), "w") as f:
        f.write(
            """[Unit]
Description=Apply screen filter

[Service]
Type=oneshot
ExecStart="/usr/bin/hyprshade" auto
"""
        )

    with open(path.join(systemd_user_config_home(), "hyprshade.timer"), "w") as f:
        on_calendar = "\n".join(
            f"OnCalendar=*-*-* {x}" for x in schedule.on_calendar_entries()
        )
        f.write(
            f"""[Unit]
Description=Apply screen filter on schedule

[Timer]
{on_calendar}
Persistent=true

[Install]
WantedBy=timers.target"""
        )

    return 0


def main():
    app()
