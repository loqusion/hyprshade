from __future__ import annotations

import os
import tomllib

from more_itertools import first_true

from .model import RootConfig
from .utils import hypr_config_home, hyprshade_config_home


class Config:
    model: RootConfig

    def __init__(self, path: str | None = None):
        path = path or Config._get_path()
        if path is None:
            raise FileNotFoundError(
                "Could not find a config file; see https://github.com/loqusion/hyprshade#scheduling"
            )
        self.model = RootConfig(Config._load(path), path=path)

    @staticmethod
    def _load(path: str) -> dict:
        with open(path, "rb") as f:
            return tomllib.load(f)

    @staticmethod
    def _get_path() -> str | None:
        candidates = [
            os.getenv("HYPRSHADE_CONFIG"),
            os.path.join(hypr_config_home(), "hyprshade.toml"),
            os.path.join(hyprshade_config_home(), "config.toml"),
        ]
        return first_true((c for c in candidates if c is not None), pred=os.path.isfile)
