from __future__ import annotations

from itertools import chain, pairwise
from typing import TYPE_CHECKING

from hyprshade.shader import Shader
from hyprshade.utils import is_time_between

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import time

    from .core import Config
    from .types import ShaderConfig, TimeRange


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

    @classmethod
    def from_config(cls, path_: str | None = None) -> Schedule:
        from .core import Config

        return cls(Config(path_))

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
