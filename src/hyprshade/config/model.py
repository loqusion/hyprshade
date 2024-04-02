# Inspired heavily by https://github.com/pypa/hatch/blob/c04877c183e850200231ed1501033a21db044d30/src/hatch/config/model.py

from __future__ import annotations

from datetime import time, timedelta
from math import ceil
from typing import Any
from typing import Final

MISSING = object()

# 30 feels like a smooth shift with a step per second
GRADUAL_SHIFT_STEPS: Final = 30

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
        self.raw_data = config_dict
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


class RootConfig(LazyConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._field_shades = MISSING

    @property
    def shades(self) -> list[ShaderConfig]:
        if self._field_shades is MISSING:
            if "shades" in self.raw_data:
                shades = self.raw_data["shades"]
                if not isinstance(shades, list):
                    self.raise_error("must be an array")

                field_shades = []
                found_default = False
                for i, shade in enumerate(shades, 1):
                    if not isinstance(shade, dict):
                        self.raise_error("must be a table", extra_steps=(str(i),))
                    if "start_time" in shade and shade.get("default") is True:
                        self.raise_error(
                            "Default shader must not define `start_time`",
                            extra_steps=(str(i),),
                        )
                    if found_default and shade.get("default") is True:
                        self.raise_error(
                            "Only one default shader is allowed",
                            extra_steps=(str(i),),
                        )
                    if "gradual_shift_duration" in shade :
                        if shade.get("start_time") is False:
                            self.raise_error(
                                "A shader with a gradual shift duration must define a `start_time`",
                                extra_steps=(str(i),),
                            )

                    if shade.get("default") is True:
                        found_default = True

                    field_shades.append(
                        ShaderConfig(shade, path=self.path, steps=("shades", str(i)))
                    )

                self._field_shades = field_shades
            else:
                self.raw_data["shades"] = []
                self._field_shades = []

        return self._field_shades  # type: ignore[return-value]

    @property
    def shaders(self) -> list[ShaderConfig]:
        return self.shades


class ShaderConfig(LazyConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._field_name = MISSING
        self._field_start_time = MISSING
        self._field_end_time = MISSING
        self._field_gradual_shift_times = MISSING
        self._field_default = MISSING
        self._field_config = MISSING

    @property
    def name(self) -> str:
        if self._field_name is MISSING:
            if "name" in self.raw_data:
                name = self.raw_data["name"]
                if not isinstance(name, str):
                    self.raise_error("must be a string")
                elif name.find(".") != -1:
                    self.raise_error(f"'{name}' must not contain a period")
                self._field_name = name
            else:
                self.raise_error("required field")

        return self._field_name  # type: ignore[return-value]

    @property
    def start_time(self) -> time | None:
        if self._field_start_time is MISSING:
            if "start_time" in self.raw_data:
                start_time = self.raw_data["start_time"]
                if not isinstance(start_time, time):
                    self.raise_error("must be time")
                self._field_start_time = start_time
            else:
                self.raw_data["start_time"] = None
                self._field_start_time = None

        return self._field_start_time  # type: ignore[return-value]

    @property
    def end_time(self) -> time | None:
        if self._field_end_time is MISSING:
            if "end_time" in self.raw_data:
                end_time = self.raw_data["end_time"]
                if not isinstance(end_time, time):
                    self.raise_error("must be time")
                self._field_end_time = end_time
            else:
                self.raw_data["end_time"] = None
                self._field_end_time = None

        return self._field_end_time  # type: ignore[return-value]

    @property
    def gradual_shift_times(self) -> list[timedelta] | None:
        if self._field_gradual_shift_times is MISSING:
            if "gradual_shift_duration" in self.raw_data:
                gradual_shift_duration = self.raw_data["gradual_shift_duration"]

                if not isinstance(gradual_shift_duration, int):
                    self.raise_error("must be an number of seconds")
                if gradual_shift_duration > 86400: # More than a day
                    self.raise_error("Gradual shift duration cannot be longer than a day")

                steps = min(gradual_shift_duration, GRADUAL_SHIFT_STEPS)
                self._field_gradual_shift_times = [timedelta(seconds=ceil(gradual_shift_duration*((i+1)/steps))) for i in range(0, steps-1)] # Remove one because start_time counts as one step
            else:
                self.raw_data["gradual_shift_duration"] = None
                self._field_gradual_shift_times = None

        return self._field_gradual_shift_times  # type: ignore[return-value]

    @property
    def default(self) -> bool:
        if self._field_default is MISSING:
            if "default" in self.raw_data:
                default = self.raw_data["default"]
                if not isinstance(default, bool):
                    self.raise_error("must be a boolean")
                self._field_default = default
            else:
                self.raw_data["default"] = False
                self._field_default = False

        return self._field_default  # type: ignore[return-value]

    @property
    def config(self) -> dict[str, Any] | None:
        if self._field_config is MISSING:
            if "config" in self.raw_data:
                config = self.raw_data["config"]
                if not isinstance(config, dict):
                    self.raise_error("must be a table")

                augmented_config = {}
                for key, value in config.items():
                    if not isinstance(key, str):
                        self.raise_error(
                            "key must be a string", extra_steps=(str(key),)
                        )
                    if isinstance(value, str):
                        value = value.upper()
                    augmented_config[key] = value

                self._field_config = augmented_config
            else:
                self.raw_data["config"] = None
                self._field_config = None

        return self._field_config  # type: ignore[return-value]
