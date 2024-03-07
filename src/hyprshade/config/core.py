from __future__ import annotations

import os
import tomllib
from os import path
from typing import cast

from more_itertools import first_true, nth, partition

from .types import ConfigDict, DefaultShadeConfig, ShaderConfig
from .utils import hypr_config_home, hyprshade_config_home


class Config:
    _dict: ConfigDict

    def __init__(self, path_: str | None = None):
        path_ = path_ or Config.get_path()
        if path_ is None:
            raise FileNotFoundError(
                "Could not find a config file; see https://github.com/loqusion/hyprshade#scheduling"
            )
        self._dict = Config._load(path_)
        self.validate()

    def validate(self) -> None:
        for shade in self._dict["shades"]:
            if not shade.get("name"):
                raise ValueError("Shade name is required")
            if not shade.get("start_time") and shade.get("default") is not True:
                raise ValueError(
                    f"Non-default shader '{shade['name']}' must define start_time"
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

    def partition(self) -> tuple[list[ShaderConfig], DefaultShadeConfig | None]:
        no_default, yes_default = partition(
            lambda s: s.get("default", False), self._dict["shades"]
        )
        rest = cast(list[ShaderConfig], list(no_default))
        default = cast(DefaultShadeConfig, nth(yes_default, 0))

        assert nth(yes_default, 0) is None, "There should be only one default shade"

        return rest, default
