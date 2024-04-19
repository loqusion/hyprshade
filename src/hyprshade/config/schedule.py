from __future__ import annotations

from dataclasses import dataclass
from itertools import chain, pairwise
from typing import TYPE_CHECKING, Any, TypeGuard

from more_itertools import only

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
                shader_conf = self.config.shader_config(entry.name)
                gradual_shift_duration = 0
                if shader_conf is not None:
                    gradual_shift_duration = shader_conf.gradual_shift_duration if shader_conf.gradual_shift_duration is not None else 0
                return Shader(entry.name, self.config.lazy_shader_variables(entry.name), gradual_shift_duration)

        return self.default_shader

    def event_times(self) -> Iterator[time]:
        yielded: set[time] = set()
        for entry in self._entries():
            if entry.start_time not in yielded:
                yielded.add(entry.start_time)
                yield entry.start_time
            if entry.end_time is not None and entry.end_time not in yielded:
                yielded.add(entry.end_time)
                yield entry.end_time

    @property
    def default_shader(self) -> Shader | None:
        default = only(filter(lambda s: s.default, self.config.model.shaders))
        if not default:
            return None
        shader_conf = self.config.shader_config(default.name)
        gradual_shift_duration = 0
        if shader_conf is not None:
            gradual_shift_duration = shader_conf.gradual_shift_duration if shader_conf.gradual_shift_duration is not None else 0
        return Shader(default.name, self.config.lazy_shader_variables(default.name), gradual_shift_duration)

    def _resolved_entries(self) -> Iterator[ResolvedEntry]:
        if not (entries := self._entries()):
            return
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
            return not shader_config.default and shader_config.start_time is not None

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
