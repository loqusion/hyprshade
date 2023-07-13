import os
from collections.abc import Iterator
from datetime import time
from itertools import chain, pairwise
from os import path
from typing import Literal, NotRequired, TypedDict, cast

import tomllib
from more_itertools import first_true, nth, partition

from .utils import hypr_config_home, hyprshade_config_home, is_time_between

TimeInterval = tuple[time, time]


class ShadeDict(TypedDict):
    name: str
    start_time: time
    end_time: NotRequired[time]


class DefaultShadeDict(TypedDict):
    name: str
    default: Literal[True]


class ConfigDict(TypedDict):
    shades: list[ShadeDict | DefaultShadeDict]


def partition_shades(
    shade_dicts: list[ShadeDict | DefaultShadeDict],
) -> tuple[DefaultShadeDict | None, list[ShadeDict]]:
    part1, part2 = partition(lambda s: s.get("default", False), shade_dicts)

    other_shades = cast(list[ShadeDict], list(part1))
    default_shade = cast(DefaultShadeDict, nth(part2, 0))

    assert nth(part2, 0) is None, "There should be only one default shade"

    return default_shade, other_shades


class ScheduleEntry:
    name: str
    start_time: time
    end_time: time | None

    def __init__(self, shade_dict: ShadeDict):
        self.name = shade_dict["name"]
        self.start_time = shade_dict["start_time"]
        self.end_time = shade_dict.get("end_time")

    def __repr__(self) -> str:
        return (
            f'ScheduleEntry("{self.name}", start_time={self.start_time}, '
            f"end_time={self.end_time})"
        )


class Schedule:
    entries: list[ScheduleEntry]
    default_shade_name: str | None

    def __init__(self, config_dict: ConfigDict):
        default_shade, other_shades = partition_shades(config_dict["shades"])
        sorted_shades = sorted(other_shades, key=lambda s: s["start_time"])
        self.entries = list(map(ScheduleEntry, sorted_shades))
        self.default_shade_name = default_shade and default_shade["name"]

    def find_shade(self, t: time) -> str | None:
        for entry_name, (start_time, end_time) in self._resolved_entries():
            if is_time_between(t, start_time, end_time):
                return entry_name

        return self.default_shade_name

    def on_calendar_entries(self) -> Iterator[time]:
        for entry in self.entries:
            yield entry.start_time
            if entry.end_time is not None:
                yield entry.end_time

    def _resolved_entries(self) -> Iterator[tuple[str, TimeInterval]]:
        for entry, next_entry in pairwise(chain(self.entries, [self.entries[0]])):
            start_time = entry.start_time
            end_time = entry.end_time or next_entry.start_time
            yield entry.name, (start_time, end_time)


class Config:
    """Parses config.toml into a dict"""

    _config_dict: ConfigDict

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = Config.get_path()
            if config_path is None:
                raise FileNotFoundError("Config file not found")

        config_dict = Config._load(config_path)
        self._config_dict = cast(ConfigDict, config_dict)

    @staticmethod
    def _load(config_path: str) -> dict[str, object]:
        with open(config_path, "rb") as f:
            return tomllib.load(f)

    @staticmethod
    def get_path() -> str | None:
        candidates = [
            os.getenv("HYPRSHADE_CONFIG"),
            path.join(hypr_config_home(), "hyprshade.toml"),
            path.join(hyprshade_config_home(), "config.toml"),
        ]
        return first_true([c for c in candidates if c is not None], pred=path.isfile)

    def to_schedule(self) -> Schedule:
        return Schedule(self._config_dict)
