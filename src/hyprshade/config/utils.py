from __future__ import annotations

import os
from os import path


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
