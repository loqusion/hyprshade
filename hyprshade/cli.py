import os
import sys
from os import path

import typer

from hyprshade.helpers import get_shader_path, get_shaders_dir

EMPTY_STR = "[[EMPTY]]"

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

    c = Config("examples/config.toml")
    for shade in c.shades:
        print(shade)

    return 0


def main():
    app()
