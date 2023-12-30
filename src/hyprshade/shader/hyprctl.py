from __future__ import annotations

import json
import subprocess
import textwrap
from json import JSONDecodeError
from typing import Final

import click

EMPTY_STR: Final = "[[EMPTY]]"


class HyprctlError(Exception):
    def __init__(self, error: subprocess.CalledProcessError, *args, **kwargs):
        command = " ".join(error.cmd)
        stdout = str(error.stdout).strip() or "<empty>"
        stderr = str(error.stderr).strip() or "<empty>"
        message = f"""hyprctl returned a non-zero exit code.

{click.style("command", fg="red")}:
{textwrap.indent(command, " " * 4)}

{click.style("stdout", fg="red")}:
{textwrap.indent(stdout, " " * 4)}

{click.style("stderr", fg="red")}:
{textwrap.indent(stderr, " " * 4)}"""

        super().__init__(message, *args, **kwargs)


def set_screen_shader(shader_path: str) -> None:
    try:
        subprocess.run(
            ["hyprctl", "keyword", "decoration:screen_shader", shader_path],
            capture_output=True,
            check=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        raise HyprctlError(e) from e


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
    except subprocess.CalledProcessError as e:
        raise HyprctlError(e) from e
    except JSONDecodeError as e:
        stdout = str(hyprctl_pipe.stdout).strip() or "<empty>"
        stderr = str(hyprctl_pipe.stderr).strip() or "<empty>"
        message = f"""hyprctl returned invalid JSON.
This is likely a bug in Hyprland; go bug Vaxry about it (nicely :)).

{click.style("stdout", fg="red")}:
{textwrap.indent(stdout, " " * 4)}

{click.style("stderr", fg="red")}:
{textwrap.indent(stderr, " " * 4)}"""

        raise RuntimeError(message) from e

    shader = str(shader_json["str"]).strip()
    if shader == EMPTY_STR:
        return None

    return shader
