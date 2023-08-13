from __future__ import annotations

import os
from os import PathLike, path
from typing import TYPE_CHECKING

from more_itertools import flatten, unique_justseen

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from datetime import time


def xdg_config_home():
    config_home = os.getenv("XDG_CONFIG_HOME")
    if config_home is None:
        home = os.getenv("HOME")
        if home is None:
            raise ValueError("$HOME environment variable is not set")
        config_home = path.join(home, ".config")
    return config_home


def hypr_config_home():
    return path.join(xdg_config_home(), "hypr")


def hyprshade_config_home():
    return path.join(xdg_config_home(), "hyprshade")


def systemd_user_config_home():
    return path.join(xdg_config_home(), "systemd/user")


def is_time_between(time_: time, start_time: time, end_time: time) -> bool:
    if end_time <= start_time:
        return start_time <= time_ or time_ <= end_time
    return start_time <= time_ <= end_time


def ls_dirs(dirs: Iterable[str | PathLike[str]]) -> Iterator[str]:
    return unique_justseen(sorted(flatten(map(os.listdir, dirs))))
