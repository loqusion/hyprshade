import os
import sysconfig
from contextlib import suppress
from functools import lru_cache
from pathlib import Path

import pytest

from hyprshade.shader import hyprctl
from hyprshade.shader.core import Shader
from tests.types import HyprshadeDirectoryName, ShaderPathFactory


@pytest.fixture(scope="session", autouse=True)
def _save_and_restore_shader():
    with suppress(hyprctl.HyprctlError, FileNotFoundError):
        screen_shader = hyprctl.get_screen_shader()

    yield

    with suppress(hyprctl.HyprctlError, FileNotFoundError):
        try:
            if screen_shader is None:
                hyprctl.clear_screen_shader()
            else:
                hyprctl.set_screen_shader(screen_shader)
        except BaseException:
            try:
                hyprctl.clear_screen_shader()
            finally:
                os.system('notify-send "hyprshade" "Failed to restore screen shader"')


class Isolation:
    def __init__(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        self.state_dir = tmp_path / "_state"
        self.config_dir = tmp_path / "_config"

        self.usr_dir = tmp_path / "_usr"

        self.hyprshade_env_dir = tmp_path / "_env"
        self.hyprshade_user_hypr_dir = self.config_dir / "hypr"
        self.hyprshade_user_hyprshade_dir = self.config_dir / "hyprshade"
        self.hyprshade_system_dir = self.usr_dir / "share/hyprshade"

        self._monkeypatch = monkeypatch

        self._old_cwd = os.getcwd()
        self.cwd = str(tmp_path)

    def __enter__(self):
        self._ensure_mkdir()

        env = {
            "XDG_CONFIG_HOME": str(self.config_dir),
            "XDG_STATE_HOME": str(self.state_dir),
            Shader.dirs.ENV_VAR_NAME: str(self.hyprshade_env_dir),
        }
        for key, value in env.items():
            self._monkeypatch.setenv(key, value)

        def _sysconfig_get_path(name: str) -> str:
            match name:
                case "data":
                    return str(self.usr_dir)
                case _:
                    raise ValueError(f"Unknown path name: {name}")

        self._monkeypatch.setattr(sysconfig, "get_path", _sysconfig_get_path)

        os.chdir(self.cwd)

        return self

    def __exit__(self, *exc):
        os.chdir(self._old_cwd)

    def shaders_dir(self, name: HyprshadeDirectoryName) -> Path:
        match name:
            case "env":
                return self.hyprshade_env_dir
            case "user_hypr":
                return self.hyprshade_user_hypr_dir / "shaders"
            case "user_hyprshade":
                return self.hyprshade_user_hyprshade_dir / "shaders"
            case "system":
                return self.hyprshade_system_dir / "shaders"
            case _:
                raise ValueError(f"Unknown directory name: {name}")

    def _ensure_mkdir(self):
        for attribute in self.__dict__.values():
            if isinstance(attribute, Path):
                attribute.mkdir(exist_ok=True, parents=True)
        for path in [
            self.hyprshade_user_hypr_dir,
            self.hyprshade_user_hyprshade_dir,
            self.hyprshade_system_dir,
        ]:
            (path / "shaders").mkdir(exist_ok=True, parents=True)


@pytest.fixture(autouse=True)
def isolation(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
):
    with Isolation(tmp_path_factory.mktemp("isolation"), monkeypatch) as i:
        yield i


@pytest.fixture()
def _clear_screen_shader():
    with suppress(hyprctl.HyprctlError, FileNotFoundError):
        hyprctl.clear_screen_shader()
    yield
    with suppress(hyprctl.HyprctlError, FileNotFoundError):
        hyprctl.clear_screen_shader()


def _write_shader(path: Path) -> Path:
    path.write_text("void main() {}")
    return path


@pytest.fixture()
def shader_path(tmp_path: Path) -> Path:
    return _write_shader(tmp_path / "shader.glsl")


@pytest.fixture()
def shader_path_factory(isolation: Isolation) -> ShaderPathFactory:
    def _shader_path(
        name: str,
        directory_name: HyprshadeDirectoryName = "system",
        *,
        extension: str = "glsl",
    ) -> Path:
        directory = isolation.shaders_dir(directory_name)
        path = directory / ".".join([name, extension])
        return _write_shader(path)

    return _shader_path


def pytest_runtest_setup(item: pytest.Item) -> None:
    for marker in item.iter_markers():
        if marker.name == "requires_hyprland" and not has_hyprland():
            pytest.skip("Not running in hyprland")


@lru_cache
def has_hyprland():
    return os.getenv("HYPRLAND_INSTANCE_SIGNATURE") is not None
