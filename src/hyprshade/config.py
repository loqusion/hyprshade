from __future__ import annotations

import os
import tomllib
from datetime import time
from itertools import chain, pairwise
from os import path
from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict, cast

from more_itertools import first_true, nth, partition

from .shader import Shader
from .utils import hypr_config_home, hyprshade_config_home, is_time_between

if TYPE_CHECKING:
    from collections.abc import Iterator

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


class ScheduleEntry:
    shader: Shader
    start_time: time
    end_time: time | None

    def __init__(self, shader_config: ShaderConfig):
        self.shader = Shader(shader_config["name"])
        self.start_time = shader_config["start_time"]
        self.end_time = shader_config.get("end_time")

    def __repr__(self) -> str:
        return (
            f'ScheduleEntry("{self.shader}", start_time={self.start_time}, '
            f"end_time={self.end_time})"
        )


class Schedule:
    entries: list[ScheduleEntry]
    default_shader: Shader | None

    def __init__(self, config: Config):
        rest_shader_configs, default_shader_config = config.partition()
        sorted_rest_shader_configs = sorted(
            rest_shader_configs, key=lambda s: s["start_time"]
        )
        self.entries = list(map(ScheduleEntry, sorted_rest_shader_configs))
        self.default_shader = (
            Shader(default_shader_config["name"])
            if default_shader_config is not None
            else None
        )

    def scheduled_shader(self, t: time) -> Shader | None:
        for shader, (start_time, end_time) in self._resolved_entries():
            if is_time_between(t, start_time, end_time):
                return shader

        return self.default_shader

    def event_times(self) -> Iterator[time]:
        for entry in self.entries:
            yield entry.start_time
            if entry.end_time is not None:
                yield entry.end_time

    def _resolved_entries(self) -> Iterator[tuple[Shader, TimeRange]]:
        for entry, next_entry in pairwise(chain(self.entries, [self.entries[0]])):
            start_time = entry.start_time
            end_time = entry.end_time or next_entry.start_time
            yield entry.shader, (start_time, end_time)


class Config:
    _dict: ConfigDict

    def __init__(self, path_: str | None = None):
        path_ = path_ or Config.get_path()
        if path_ is None:
            raise FileNotFoundError("Config file not found")
        self._dict = Config._load(path_)

    @staticmethod
    def _load(path_: str) -> ConfigDict:
        with open(path_, "rb") as f:
            return cast(ConfigDict, tomllib.load(f))

    @staticmethod
    def get_path() -> str | None:
        candidates = [
            os.getenv("HYPRSHADE_CONFIG"),
            path.join(hypr_config_home(), "hyprshade.toml"),
            path.join(hyprshade_config_home(), "config.toml"),
        ]
        return first_true((c for c in candidates if c is not None), pred=path.isfile)

    def partition(self) -> tuple[list[ShaderConfig], DefaultShadeConfig | None]:
        no_default, yes_default = partition(
            lambda s: s.get("default", False), self._dict["shades"]
        )
        rest = cast(list[ShaderConfig], list(no_default))
        default = cast(DefaultShadeConfig, nth(yes_default, 0))

        # TODO: Should raise an exception instead of asserting
        assert nth(yes_default, 0) is None, "There should be only one default shade"

        return rest, default

    def to_schedule(self) -> Schedule:
        return Schedule(self)
