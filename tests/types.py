from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from typing_extensions import Protocol

if TYPE_CHECKING:
    from pathlib import Path

    from hyprshade.config.core import Config
    from tests.conftest import Isolation


HyprshadeDirectoryName = Literal["env", "user_hypr", "user_hyprshade", "system"]
ConfigPathName = Literal["user_hypr", "user_hyprshade"]


class ShaderPathFactory(Protocol):
    def __call__(
        self,
        name: str,
        directory_name: HyprshadeDirectoryName = "system",
        *,
        extension: str = "glsl",
        text: str | None = None,
    ) -> Path: ...


class ConfigFactory:
    _isolation: Isolation
    _path: Path

    def __init__(self, isolation: Isolation):
        self._isolation = isolation
        self.set_path("user_hypr")

    @property
    def path(self) -> Path:
        return self._path

    def set_path(self, config_path_name: ConfigPathName) -> None:
        match config_path_name:
            case "user_hypr":
                self._path = self._isolation.hyprshade_user_hypr_dir / "hyprshade.toml"
            case "user_hyrpshade":
                self._path = (
                    self._isolation.hyprshade_user_hyprshade_dir / "config.toml"
                )
            case _:
                raise ValueError(f"Unknown config path name: {config_path_name}")

    def write(self, data: dict) -> None:
        import tomlkit

        with open(self._path, "w") as f:
            tomlkit.dump(data, f)

    def get_config(self) -> Config:
        from hyprshade.config.core import Config

        return Config(str(self._path))
