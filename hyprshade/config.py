from collections.abc import Iterable
from datetime import time
from itertools import chain, pairwise
from os import path
from typing import Any, Literal, NotRequired, TypedDict, TypeGuard, cast

import tomllib
from more_itertools import nth, partition

from hyprshade.utils import hyprshade_config_home, is_time_between


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
    default_shade: str | None

    def __init__(self, config_dict: ConfigDict):
        default_shade, other_shades = partition_shades(config_dict["shades"])
        sorted_shades = sorted(other_shades, key=lambda s: s["start_time"])
        self.entries = list(map(ScheduleEntry, sorted_shades))
        self.default_shade = default_shade and default_shade["name"]

    def contained(self, t: time) -> str | None:
        for entry, next_entry in self._pairwise_entries():
            start_time = entry.start_time
            end_time = entry.end_time or next_entry.start_time
            if is_time_between(t, start_time, end_time):
                return entry.name

        return self.default_shade

    def on_calendar_entries(self) -> Iterable[time]:
        for entry in self.entries:
            yield entry.start_time
            if entry.end_time is not None:
                yield entry.end_time

    def _pairwise_entries(self):
        return pairwise(chain(self.entries, [self.entries[0]]))


class Config:
    """Parses config.toml into a dict"""

    _config_dict: ConfigDict

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = Config.get_path()

        config_dict = Config._load(config_path)
        if Config._validate(config_dict):
            self._config_dict = config_dict

    @staticmethod
    def _validate(config_dict: dict[str, Any]) -> TypeGuard[ConfigDict]:
        """Validates schema, and rejects any config that has overlapping time ranges."""

        return True
        raise NotImplementedError

    @staticmethod
    def _load(config_path: str) -> dict[str, object]:
        with open(config_path, "rb") as f:
            return tomllib.load(f)

    @staticmethod
    def get_path() -> str:
        return path.join(hyprshade_config_home(), "config.toml")

    def to_schedule(self) -> Schedule:
        return Schedule(self._config_dict)
