from __future__ import annotations

from os import path
from typing import Literal

from hyprshade.utils import systemd_user_config_home

SystemdUnitType = Literal["service", "timer"]


def write_systemd_user_unit(unit_type: SystemdUnitType, body: str):
    with open(
        path.join(systemd_user_config_home(), f"hyprshade.{unit_type}"), "w"
    ) as f:
        f.write(body)
