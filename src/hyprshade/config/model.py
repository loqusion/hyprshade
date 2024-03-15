# Inspired heavily by https://github.com/pypa/hatch/blob/c04877c183e850200231ed1501033a21db044d30/src/hatch/config/model.py

from __future__ import annotations

from datetime import time
from typing import final

MISSING = object()


class ConfigError(Exception):
    def __init__(self, *args, location: str, path: str):
        self.location = location
        self.path = path
        super().__init__(*args)

    def __str__(self):
        return f"Failed to parse {self.path}:\n{self.location}\n  {super().__str__()}"


def parse_config(obj):
    if isinstance(obj, LazyConfig):
        obj.parse_fields()
    elif isinstance(obj, list):
        for o in obj:
            parse_config(o)
    elif isinstance(obj, dict):
        for o in obj.values():
            parse_config(o)


class LazyConfig:
    def __init__(self, config_dict: dict, *, path: str, steps: tuple = ()):
        self._dict = config_dict
        self.path = path
        self.steps = steps

    def parse_fields(self):
        for attribute in self.__dict__:
            _, prefix, name = attribute.partition("_field_")
            if prefix:
                parse_config(getattr(self, name))

    def raise_error(self, message, *, extra_steps: tuple = ()):
        import inspect

        field = inspect.currentframe().f_back.f_code.co_name  # type: ignore[union-attr]
        raise ConfigError(
            message,
            location=" -> ".join([*self.steps, field, *extra_steps]),
            path=self.path,
        )


@final
class RootConfig(LazyConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._field_shades = MISSING

    @property
    def shades(self) -> list[ShaderConfig]:
        if self._field_shades is MISSING:
            if "shades" in self._dict:
                shades = self._dict["shades"]
                if isinstance(shades, list):
                    self._field_shades = [
                        ShaderConfig(s, path=self.path, steps=("shades",))
                        for s in shades
                    ]
                else:
                    self.raise_error("must be an array")
            else:
                self._dict["shades"] = []
                self._field_shades = []

        return self._field_shades  # type: ignore[return-value]

    @property
    def shaders(self) -> list[ShaderConfig]:
        return self.shades


@final
class ShaderConfig(LazyConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._field_name = MISSING
        self._field_start_time = MISSING
        self._field_end_time = MISSING
        self._field_default = MISSING

    @property
    def name(self) -> str:
        if self._field_name is MISSING:
            if "name" in self._dict:
                name = self._dict["name"]
                if not isinstance(name, str):
                    self.raise_error("must be a string")
                self._field_name = name
            else:
                self.raise_error("required field")

        return self._field_name  # type: ignore[return-value]

    @property
    def start_time(self) -> time | None:
        if self._field_start_time is MISSING:
            if "start_time" in self._dict:
                start_time = self._dict["start_time"]
                if not isinstance(start_time, time):
                    self.raise_error("must be time")
                self._field_start_time = start_time
            else:
                self._dict["start_time"] = None
                self._field_start_time = None

        return self._field_start_time  # type: ignore[return-value]

    @property
    def end_time(self) -> time | None:
        if self._field_end_time is MISSING:
            if "end_time" in self._dict:
                end_time = self._dict["end_time"]
                if not isinstance(end_time, time):
                    self.raise_error("must be time")
                self._field_end_time = end_time
            else:
                self._dict["end_time"] = None
                self._field_end_time = None

        return self._field_end_time  # type: ignore[return-value]

    @property
    def default(self) -> bool:
        if self._field_default is MISSING:
            if "default" in self._dict:
                default = self._dict["default"]
                if not isinstance(default, bool):
                    self.raise_error("must be a boolean")
                self._field_default = default
            else:
                self._dict["default"] = False
                self._field_default = False

        return self._field_default  # type: ignore[return-value]
