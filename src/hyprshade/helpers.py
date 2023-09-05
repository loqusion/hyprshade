from __future__ import annotations

import os
from os import path
from typing import Literal

from hyprshade.utils import systemd_user_config_home

SystemdUnitType = Literal["service", "timer"]


def write_systemd_user_unit(unit_type: SystemdUnitType, body: str):
    dest_dir = systemd_user_config_home()
    os.makedirs(dest_dir, exist_ok=True)
    with open(path.join(dest_dir, f"hyprshade.{unit_type}"), "w") as f:
        f.write(body)
