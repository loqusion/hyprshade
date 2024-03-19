from __future__ import annotations

from dataclasses import dataclass
from itertools import chain, pairwise
from typing import TYPE_CHECKING, Any, TypeGuard

from hyprshade.shader.core import Shader
from hyprshade.utils.time import is_time_between

from .model import ShaderConfig

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import time

    from .core import Config


class Schedule:
    config: Config

    def __init__(self, config: Config):
        self.config = config

    def scheduled_shader(self, t: time) -> Shader | None:
        for entry in self._resolved_entries():
            if is_time_between(t, entry.start_time, entry.end_time):
                return Shader(entry.name, self.config)

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
        return Shader(default.name, self.config) if default else None

    def _resolved_entries(self) -> Iterator[ResolvedEntry]:
        if not (entries := self._entries()):
            return iter(())
        for entry, next_entry in pairwise(chain(entries, [entries[0]])):
            yield ResolvedEntry(
                name=entry.name,
                start_time=entry.start_time,
                end_time=entry.end_time or next_entry.start_time,
                config=entry.config,
            )

    def _entries(self) -> list[ScheduledShaderConfig]:
        def has_schedule(
            shader_config: ShaderConfig,
        ) -> TypeGuard[ScheduledShaderConfig]:
            if not shader_config.default:
                assert shader_config.start_time is not None
                return True
            return False

        filtered = filter(has_schedule, self.config.model.shaders)
        return sorted(filtered, key=lambda s: s.start_time)


class ScheduledShaderConfig(ShaderConfig):
    start_time: time


@dataclass()
class ResolvedEntry:
    name: str
    start_time: time
    end_time: time
    config: dict[str, Any] | None
