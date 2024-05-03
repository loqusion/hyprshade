# Inspired heavily by https://github.com/pypa/hatch/blob/c04877c183e850200231ed1501033a21db044d30/src/hatch/config/model.py

from __future__ import annotations

from datetime import time
from typing import Any

from hyprshade.template import mustache

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
        self._raise_error_impl(message, (*self.steps, field, *extra_steps))

    def _raise_error_impl(self, message, steps: tuple):
        raise ConfigError(message, location=" -> ".join(steps), path=self.path)


class RootConfig(LazyConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._field_shaders = MISSING

    @property
    def shaders(self) -> list[ShaderConfig]:
        if self._field_shaders is MISSING:
            # NOTE: `shades` is deprecated but still supported
            if "shaders" in self.raw_data or "shades" in self.raw_data:
                shaders = self.raw_data.get("shaders", [])
                shades = self.raw_data.get("shades", [])
                if not isinstance(shaders, list):
                    self.raise_error("must be an array")
                if not isinstance(shades, list):
                    self._raise_error_impl("must be an array", ("shades",))

                field_shaders = []
                found_default = False
                for step, shaders_array in zip(
                    ["shaders", "shades"], [shaders, shades], strict=True
                ):
                    for i, shader in enumerate(shaders_array, 1):
                        if not isinstance(shader, dict):
                            self._raise_error_impl("must be a table", (step, str(i)))
                        if "start_time" in shader and shader.get("default") is True:
                            self._raise_error_impl(
                                "Default shader must not define `start_time`",
                                (step, str(i)),
                            )
                        if (
                            "start_time" in shader
                            and "end_time" in shader
                            and shader.get("start_time") == shader.get("end_time")
                        ):
                            self._raise_error_impl(
                                "`start_time` and `end_time` must not be the same",
                                (step, str(i)),
                            )
                        if found_default and shader.get("default") is True:
                            self._raise_error_impl(
                                "Only one default shader is allowed",
                                (step, str(i)),
                            )

                        if shader.get("default") is True:
                            found_default = True

                        field_shaders.append(
                            ShaderConfig(shader, path=self.path, steps=(step, str(i)))
                        )

                self._field_shaders = field_shaders
            else:
                self.raw_data["shaders"] = []
                self._field_shaders = []

        return self._field_shaders  # type: ignore[return-value]


class ShaderConfig(LazyConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._field_name = MISSING
        self._field_start_time = MISSING
        self._field_end_time = MISSING
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
                    if key in mustache.DEFAULT_RENDER_DATA:
                        self.raise_error(
                            f"key '{key}' is reserved", extra_steps=(str(key),)
                        )
                    augmented_config[key] = value

                self._field_config = augmented_config
            else:
                self.raw_data["config"] = None
                self._field_config = None

        return self._field_config  # type: ignore[return-value]
