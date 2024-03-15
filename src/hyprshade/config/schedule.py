from __future__ import annotations

from itertools import chain, pairwise
from typing import TYPE_CHECKING, TypeGuard

from hyprshade.shader.core import Shader
from hyprshade.utils import is_time_between

from .model import ShaderConfig

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import time

    from .core import Config

    TimeRange = tuple[time, time]


class Schedule:
    config: Config

    def __init__(self, config: Config):
        self.config = config

    @classmethod
    def from_config(cls, path: str | None = None) -> Schedule:
        from .core import Config

        return cls(Config(path))

    def scheduled_shader(self, t: time) -> Shader | None:
        for shader_name, (start_time, end_time) in self._resolved_entries():
            if is_time_between(t, start_time, end_time):
                return Shader(shader_name)

        return self.default_shader

    def event_times(self) -> Iterator[time]:
        for entry in self._entries():
            yield entry.start_time
            if entry.end_time is not None:
                yield entry.end_time

    @property
    def default_shader(self) -> Shader | None:
        filtered = filter(lambda s: s.default, self.config.model.shaders)
        default = next(filtered, None)
        assert next(filtered, None) is None
        return Shader(default.name) if default else None

    def _resolved_entries(self) -> Iterator[tuple[str, TimeRange]]:
        if not (entries := self._entries()):
            return iter(())
        for entry, next_entry in pairwise(chain(entries, [entries[0]])):
            name = entry.name
            start_time = entry.start_time
            end_time = entry.end_time or next_entry.start_time
            yield name, (start_time, end_time)

    def _entries(self) -> list[ScheduledShaderConfig]:
        def has_schedule(
            shader_config: ShaderConfig
        ) -> TypeGuard[ScheduledShaderConfig]:
            if not shader_config.default:
                assert shader_config.start_time is not None
                return True
            return False

        filtered = filter(has_schedule, self.config.model.shaders)
        return sorted(filtered, key=lambda s: s.start_time)


class ScheduledShaderConfig(ShaderConfig):
    start_time: time
