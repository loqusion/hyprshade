from __future__ import annotations

import os
import tomllib
from os import path

from more_itertools import first_true

from .model import RootConfig
from .utils import hypr_config_home, hyprshade_config_home


class Config:
    model: RootConfig

    def __init__(self, path_: str | None = None):
        path_ = path_ or Config._get_path()
        if path_ is None:
            raise FileNotFoundError(
                "Could not find a config file; see https://github.com/loqusion/hyprshade#scheduling"
            )
        self.model = RootConfig(Config._load(path_), path=path_)

    @staticmethod
    def _load(path_: str) -> dict:
        with open(path_, "rb") as f:
            return tomllib.load(f)

    @staticmethod
    def _get_path() -> str | None:
        candidates = [
            os.getenv("HYPRSHADE_CONFIG"),
            path.join(hypr_config_home(), "hyprshade.toml"),
            path.join(hyprshade_config_home(), "config.toml"),
        ]
        return first_true((c for c in candidates if c is not None), pred=path.isfile)
