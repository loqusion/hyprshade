from __future__ import annotations

import json
import subprocess
from json import JSONDecodeError
from typing import Final

EMPTY_STR: Final = "[[EMPTY]]"


def set_screen_shader(shader_path: str) -> None:
    subprocess.run(
        ["hyprctl", "keyword", "decoration:screen_shader", shader_path],
        capture_output=True,
        check=True,
    )


def clear_screen_shader() -> None:
    set_screen_shader(EMPTY_STR)


def get_screen_shader() -> str | None:
    try:
        hyprctl_pipe = subprocess.run(
            ["hyprctl", "-j", "getoption", "decoration:screen_shader"],
            capture_output=True,
            check=True,
            encoding="utf-8",
        )
        shader_json = json.loads(hyprctl_pipe.stdout)
    except JSONDecodeError as e:
        message = f"""hyprctl returned invalid JSON.
This is likely a bug in Hyprland; go bug Vaxry about it (nicely :)).

stdout:
{hyprctl_pipe.stdout}
stderr:
{hyprctl_pipe.stderr}"""
        raise RuntimeError(message) from e

    shader = str(shader_json["str"]).strip()
    if shader == EMPTY_STR:
        return None

    return shader
