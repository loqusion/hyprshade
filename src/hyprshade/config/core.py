from __future__ import annotations

import os
import tomllib
from typing import Any, Never

from more_itertools import first_true

from hyprshade.utils.xdg import user_config_dir

from .model import RootConfig, ShaderConfig


class Config:
    model: RootConfig

    def __init__(self, path: str | None = None):
        path = path or Config._get_path()
        if path is None:
            self.raise_not_found()
        self.model = RootConfig(Config._load(path), path=path)

    def shader_config(self, name_or_path: str) -> ShaderConfig | None:
        from hyprshade.shader.core import Shader

        name = Shader.path_to_name(name_or_path)
        return first_true(self.model.shaders, pred=lambda s: s.name == name)

    def shader_variables(self, name_or_path: str) -> dict[str, Any] | None:
        shader_config = self.shader_config(name_or_path)
        return shader_config.config if shader_config else None

    @staticmethod
    def raise_not_found() -> Never:
        raise FileNotFoundError(
            "Could not find a config file; see https://github.com/loqusion/hyprshade#scheduling"
        )

    @staticmethod
    def _load(path: str) -> dict:
        with open(path, "rb") as f:
            return tomllib.load(f)

    @staticmethod
    def _get_path() -> str | None:
        candidates = [
            os.getenv("HYPRSHADE_CONFIG"),
            os.path.join(user_config_dir("hypr"), "hyprshade.toml"),
            os.path.join(user_config_dir("hyprshade"), "config.toml"),
        ]
        return first_true((c for c in candidates if c is not None), pred=os.path.isfile)
