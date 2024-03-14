from __future__ import annotations

import os
import tomllib
from os import path
from typing import cast

from more_itertools import first_true, nth, partition

from .types import ConfigDict, DefaultShadeConfig, ShaderConfig
from .utils import hypr_config_home, hyprshade_config_home


class Config:
    _config_path: str
    _dict: ConfigDict

    def __init__(self, path_: str | None = None):
        path_ = path_ or Config.get_path()
        if path_ is None:
            raise FileNotFoundError(
                "Could not find a config file; see https://github.com/loqusion/hyprshade#scheduling"
            )
        self._config_path = path_
        self._dict = Config._load(path_)
        self._validate()

    def partition(self) -> tuple[list[ShaderConfig], DefaultShadeConfig | None]:
        no_default, yes_default = partition(
            lambda s: s.get("default", False), self._dict["shades"]
        )
        rest = cast(list[ShaderConfig], list(no_default))
        default = cast(DefaultShadeConfig, nth(yes_default, 0))

        assert nth(yes_default, 0) is None, "There should be only one default shade"

        return rest, default

    def _validate(self) -> None:
        shaders = self._dict.get("shades", [])
        if not isinstance(shaders, list):
            raise ConfigError(self._config_path, "`shades` must be a list")
        for shader in shaders:
            if not shader.get("name"):
                raise ConfigError(
                    self._config_path, "`name` is required for each item in `shades`"
                )
            if not shader.get("start_time") and shader.get("default") is not True:
                raise ConfigError(
                    self._config_path,
                    f"Non-default shader '{shader['name']}' must define `start_time`",
                )

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


class ConfigError(Exception):
    def __init__(self, config_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = config_path

    def __str__(self) -> str:
        msg = super().__str__()
        return f"Failed to parse {self.config_path}: {msg}"
