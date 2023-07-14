import json
import os
from json import JSONDecodeError
from os import path
from typing import Final

EMPTY_STR: Final = "[[EMPTY]]"


def set_screen_shader(shader_path: str) -> int:
    return os.system(f"hyprctl keyword decoration:screen_shader '{shader_path}'")


def clear_screen_shader() -> int:
    return set_screen_shader(EMPTY_STR)


def get_screen_shader() -> str | None:
    try:
        o = json.load(os.popen("hyprctl -j getoption decoration:screen_shader"))
    except JSONDecodeError as e:
        raise RuntimeError("Failed to parse JSON returned by hyprctl") from e

    shader = str(o["str"]).strip()
    if shader == EMPTY_STR:
        return None
    if not path.isfile(shader):
        raise RuntimeError(f"Got shader {shader} from hyprctl, which does not exist")

    return shader
