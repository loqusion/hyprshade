from __future__ import annotations

from datetime import datetime

import click
from more_itertools import quantify

from hyprshade.config.schedule import Schedule
from hyprshade.shader.core import Shader

from .utils import ContextObject, ShaderParamType, optional_param


def get_shader_to_toggle(
    shader: Shader | None, fallback: Shader | None
) -> Shader | None:
    current = Shader.current()
    if shader != current:
        return shader
    return fallback


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


@click.command(short_help="Toggle screen shader")
@click.argument(
    "shader",
    type=ShaderParamType(),
    **optional_param("SHADER"),
)
@click.option(
    "--fallback",
    metavar="SHADER",
    type=ShaderParamType(),
    help="Select fallback shader",
)
@click.option(
    "--fallback-default",
    is_flag=True,
    default=False,
    help="Use default shader as fallback",
)
@click.option(
    "--fallback-auto",
    is_flag=True,
    default=False,
    help="Automatically infer fallback",
)
@click.pass_obj
def toggle(
    obj: ContextObject,
    shader: Shader | None,
    fallback: Shader | None,
    fallback_default: bool,
    fallback_auto: bool,
):
    """Toggle screen shader.

    The default behavior is to toggle between SHADER and off. If SHADER is
    not provided, it is inferred from schedule configuration.

    When a fallback shader is provided with one of the --fallback* options, the
    toggle will be between SHADER and the fallback shader.

    --fallback-auto will determine the fallback from the schedule configuration.
    If the currently scheduled shader and SHADER are identical, the fallback
    will instead be the default shader.
    """

    t = datetime.now().time()
    config = obj.get_config(raising=(fallback_default or fallback_auto))

    fallback_opts = [fallback, fallback_default, fallback_auto]
    if quantify(fallback_opts) > 1:
        raise click.BadOptionUsage(
            "--fallback", "Must not specify more than one --fallback* option"
        )

    schedule = Schedule(config) if config is not None else None
    scheduled = schedule.scheduled_shader(t) if schedule is not None else None
    default = schedule.default_shader if schedule is not None else None
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
