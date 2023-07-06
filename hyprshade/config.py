from datetime import time
from typing import Any, TypeVar

import tomllib

K = TypeVar("K")
V = TypeVar("V")


class ShadeConfig:
    name: str
    start_time: time
    shade_config: dict

    def __init__(self, shade_config: dict):
        self.name = shade_config["name"]
        self.start_time = shade_config["start_time"]
        self.shade_config = shade_config

    def __repr__(self) -> str:
        return f"ShadeConfig({self.shade_config})"


class Config:
    shades: list[ShadeConfig]

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = Config.get_path()
        config = Config.load(config_path)
        shades_list: list = config["shades"]
        self.shades = list(map(ShadeConfig, shades_list))

    @staticmethod
    def load(config_path: str) -> dict[str, Any]:
        with open(config_path, "rb") as f:
            return tomllib.load(f)

    @staticmethod
    def get_path() -> str:
        return "config.toml"
