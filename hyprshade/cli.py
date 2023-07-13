import os
from datetime import datetime
from itertools import chain
from os import path

import typer

from .constants import SHADER_DIRS
from .helpers import resolve_shader_path
from .hyprctl import clear_screen_shader, get_screen_shader, set_screen_shader
from .utils import systemd_user_config_home

app = typer.Typer(no_args_is_help=True)


@app.command()
def on(shader_name_or_path: str) -> int:
    """Turn on screen shader"""

    shader_path = resolve_shader_path(shader_name_or_path)
    return set_screen_shader(shader_path)


@app.command()
def off() -> int:
    """Turn off screen shader"""

    return clear_screen_shader()


@app.command()
def toggle(shader_name_or_path: str) -> int:
    """Toggle screen shader"""

    current_shader = get_screen_shader()
    if current_shader is not None and path.samefile(
        resolve_shader_path(shader_name_or_path), current_shader
    ):
        return off()

    return on(shader_name_or_path)


@app.command()
def auto() -> int:
    """Turn on/off screen shader based on schedule"""

    from hyprshade.config import Config

    t = datetime.now().time()
    schedule = Config().to_schedule()
    shade = schedule.find_shade(t)

    if shade is not None:
        return on(shade)
    return off()


@app.command()
def install() -> int:
    """Instal systemd user units"""

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
            sorted([f"OnCalendar=*-*-* {x}" for x in schedule.on_calendar_entries()])
        )
        f.write(
            f"""[Unit]
Description=Apply screen filter on schedule

[Timer]
{on_calendar}

[Install]
WantedBy=timers.target"""
        )

    return 0


@app.command()
def ls() -> int:
    """List available screen shaders"""

    current_shader = get_screen_shader()
    shader_base = path.basename(current_shader) if current_shader else None

    for shader in chain(
        *map(
            os.listdir,
            SHADER_DIRS,
        )
    ):
        c = "*" if shader == shader_base else " "
        shader, _ = path.splitext(shader)
        print(f"{c} {shader}")

    return 0


def main():
    app()
