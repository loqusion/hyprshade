from __future__ import annotations

import logging
import sys
from datetime import datetime, time

import click
from more_itertools import quantify

from .click_utils import convert_to_shader, optional_param
from .config import Config
from .helpers import write_systemd_user_unit
from .shader import Shader
from .utils import ls_dirs


@click.group()
@click.version_option()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output.")
def cli(verbose: bool):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level)


def main():
    try:
        cli()
    except Exception as e:
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            raise e
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("shader", callback=convert_to_shader)
def on(shader: Shader):
    """Turn on screen shader."""

    shader.on()


@cli.command()
def off():
    """Turn off screen shader."""

    Shader.off()


def get_shader_to_toggle(
    shader: Shader | None, fallback: Shader | None
) -> Shader | None:
    current = Shader.current()
    if shader == current:
        return fallback
    return shader


def get_fallback(
    *,
    shader: Shader | None,
    default: Shader | None,
    auto: Shader | None,
    fallback_default: bool,
    fallback_auto: bool,
) -> Shader | None:
    if fallback_default or (fallback_auto and shader == auto):
        return default
    elif fallback_auto:
        return auto
    return None


def try_from_config(t: time, panic: bool) -> tuple[Shader | None, Shader | None]:
    try:
        schedule = Config().to_schedule()
    except FileNotFoundError:
        if panic:
            raise
        return None, None
    return schedule.scheduled_shader(t), schedule.default_shader


@cli.command()
@click.argument("shader", **optional_param("SHADER", convert_to_shader))
@click.option(
    "--fallback",
    metavar="SHADER",
    callback=convert_to_shader,
    help="Shader to switch to instead of toggling off.",
)
@click.option(
    "--fallback-default",
    is_flag=True,
    default=False,
    help="Use default shader as fallback.",
)
@click.option(
    "--fallback-auto",
    is_flag=True,
    default=False,
    help="Use currently scheduled shader as fallback. Equivalent to --fallback-default"
    " when the currently scheduled shader is SHADER.",
)
def toggle(
    shader: Shader | None,
    fallback: Shader | None,
    fallback_default: bool,
    fallback_auto: bool,
):
    """Toggle screen shader.

    If run with no arguments, SHADER is inferred based on schedule.

    When a fallback shader is specified, will instead toggle between SHADER
    and the fallback shader.
    """

    t = datetime.now().time()

    fallback_opts = [fallback, fallback_default, fallback_auto]
    if quantify(fallback_opts) > 1:
        raise click.BadOptionUsage(
            "--fallback", "Cannot specify more than 1 --fallback* option"
        )

    scheduled, default = try_from_config(t, fallback_default or fallback_auto)
    shader = shader or scheduled

    fallback = fallback or get_fallback(
        shader=shader,
        default=default,
        auto=scheduled,
        fallback_default=fallback_default,
        fallback_auto=fallback_auto,
    )
    shader_to_toggle = get_shader_to_toggle(shader, fallback)
    if shader_to_toggle:
        shader_to_toggle.on()
    else:
        Shader.off()


@cli.command()
@click.pass_context
def auto(ctx: click.Context):
    """Turn on/off screen shader based on schedule."""

    t = datetime.now().time()
    shader = Config().to_schedule().scheduled_shader(t)

    if shader:
        shader.on()
    else:
        Shader.off()


@cli.command()
def install():
    """Install systemd user units."""

    schedule = Config().to_schedule()
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


@cli.command()
def ls():
    """List available screen shaders."""

    current = Shader.current()

    for shader in map(Shader, ls_dirs(Shader.dirs.all())):
        c = "*" if shader == current else " "
        click.echo(f"{c} {shader}")
