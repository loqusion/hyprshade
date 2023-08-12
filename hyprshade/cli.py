import logging
import sys
from datetime import datetime

import click
from more_itertools import quantify

from .click_utils import convert_to_shader, optional_param
from .constants import SHADER_DIRS
from .helpers import schedule_from_config, write_systemd_user_unit
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
    help="Use default shader as fallback. (see --fallback)",
)
@click.option(
    "--fallback-auto",
    is_flag=True,
    default=False,
    help="Use currently scheduled shader as fallback."
    " (If the currently scheduled shader is SHADER_NAME_OR_PATH, the default"
    " shader will be used as the fallback instead.)",
)
def toggle(
    shader: Shader | None,
    fallback: Shader | None,
    fallback_default: bool,
    fallback_auto: bool,
):
    """Toggle screen shader.

    If run with no arguments, SHADER_NAME_OR_PATH is inferred based on schedule.

    When --fallback is specified, will toggle between SHADER_NAME_OR_PATH and the
    fallback shader. --fallback-default will toggle between SHADER_NAME_OR_PATH and the
    default shader, whereas --fallback-auto will toggle between SHADER_NAME_OR_PATH and
    the currently scheduled shader. (--fallback-auto is equivalent to --fallback-default
    if the currently scheduled shader is SHADER_NAME_OR_PATH.)
    """

    t = datetime.now().time()

    fallback_opts = [fallback, fallback_default, fallback_auto]
    if quantify(fallback_opts) > 1:
        raise click.BadOptionUsage(
            "--fallback", "Cannot specify more than 1 --fallback* option"
        )

    current = Shader.current()
    try:
        schedule = schedule_from_config()
        scheduled_shader = schedule.scheduled_shader(t)
    except FileNotFoundError:
        schedule = None
        scheduled_shader = None
    shader = shader or scheduled_shader

    def get_fallback() -> Shader | None:
        if not schedule:
            return fallback
        if fallback_default or (
            fallback_auto
            and shader
            and scheduled_shader
            and shader.samefile(scheduled_shader)
        ):
            return schedule.default_shader
        elif fallback_auto:
            return scheduled_shader
        return fallback

    fallback = get_fallback()
    toggle_off = Shader.off if fallback is None else fallback.on

    if current is not None and shader is not None and shader.samefile(current):
        toggle_off()
    elif shader is not None:
        shader.on()


@cli.command()
@click.pass_context
def auto(ctx: click.Context):
    """Turn on/off screen shader based on schedule."""

    t = datetime.now().time()
    shader = schedule_from_config().scheduled_shader(t)

    if shader is None:
        Shader.off()
    else:
        shader.on()


@cli.command()
def install():
    """Install systemd user units."""

    schedule = schedule_from_config()
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

    for shader in map(Shader, ls_dirs(SHADER_DIRS)):
        c = "*" if current is not None and shader.samefile(current) else " "
        click.echo(f"{c} {shader}")
