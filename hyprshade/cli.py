import os
import sys
from datetime import datetime
from functools import cache
from itertools import chain
from os import path

import click

from .constants import SHADER_DIRS
from .helpers import resolve_shader_path
from .hyprctl import clear_screen_shader, get_screen_shader, set_screen_shader
from .utils import systemd_user_config_home


@click.group()
def cli():
    pass


def main():
    try:
        cli()
    except Exception as e:
        click.echo(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command()
@click.argument("shader_name_or_path")
def on(shader_name_or_path: str):
    """Turn on screen shader."""

    shader_path = resolve_shader_path(shader_name_or_path)
    set_screen_shader(shader_path)


@cli.command()
def off():
    """Turn off screen shader."""

    clear_screen_shader()


@cli.command()
@click.argument("shader_name_or_path", default=None)
@click.option(
    "--fallback",
    metavar="SHADER",
    help="Shader to switch to instead of toggling off.",
)
@click.option(
    "--fallback-default",
    is_flag=True,
    default=False,
    help="Use default shader as fallback. (see --fallback)",
)
@click.pass_context
def toggle(
    ctx: click.Context,
    shader_name_or_path: str | None,
    fallback: str | None,
    fallback_default: bool,
):
    """Toggle screen shader.

    If run with no arguments, SHADER_NAME_OR_PATH is inferred based on schedule.

    When --fallback is specified, will toggle between SHADER_NAME_OR_PATH and the
    fallback shader. --fallback-default will toggle between SHADER_NAME_OR_PATH and the
    default shader.
    """

    from .config import Schedule

    @cache
    def schedule() -> Schedule:
        from .config import Config

        try:
            return Config().to_schedule()
        except FileNotFoundError as e:
            click.echo(f"Error: {e}")
            sys.exit(1)

    if fallback and fallback_default:
        raise click.BadOptionUsage(
            "--fallback", "Cannot specify both --fallback and --fallback-default"
        )

    t = datetime.now().time()

    if fallback_default:
        fallback = schedule().default_shade_name

    def toggle_off():
        if fallback is None:
            ctx.invoke(off)
            ctx.exit()
        else:
            ctx.invoke(on, shader_name_or_path=fallback)
            ctx.exit()

    shade = shader_name_or_path or schedule().find_shade(t)
    if shade is None:
        ctx.invoke(off)
        ctx.exit()
    shade = resolve_shader_path(shade)

    current_shader = get_screen_shader()
    if current_shader is not None and path.samefile(shade, current_shader):
        toggle_off()
        ctx.exit()

    ctx.invoke(on, shader_name_or_path=shade)


@cli.command()
@click.pass_context
def auto(ctx):
    """Turn on/off screen shader based on schedule."""

    from .config import Config

    t = datetime.now().time()
    shade = Config().to_schedule().find_shade(t)

    if shade is not None:
        ctx.invoke(on, shade_or_path=shade)
        ctx.exit()
    ctx.invoke(off)


@cli.command()
def install():
    """Install systemd user units."""

    from .config import Config

    schedule = Config().to_schedule()

    with open(path.join(systemd_user_config_home(), "hyprshade.service"), "w") as f:
        f.write(
            """[Unit]
Description=Apply screen filter

[Service]
Type=oneshot
ExecStart="/usr/bin/hyprshade" auto"""
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


@cli.command()
def ls():
    """List available screen shaders."""

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
        click.echo(f"{c} {shader}")
