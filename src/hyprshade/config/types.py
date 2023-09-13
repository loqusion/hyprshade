from __future__ import annotations

from datetime import time
from typing import Literal, NotRequired, TypedDict

TimeRange = tuple[time, time]


class ShaderConfig(TypedDict):
    name: str
    start_time: time
    end_time: NotRequired[time]


class DefaultShadeConfig(TypedDict):
    name: str
    default: Literal[True]


class ConfigDict(TypedDict):
    shades: list[ShaderConfig | DefaultShadeConfig]
