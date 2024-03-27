import os
import sysconfig
from contextlib import suppress
from functools import lru_cache
from pathlib import Path

import pytest

from hyprshade.shader import hyprctl
from hyprshade.shader.core import Shader
from tests.types import ShaderPathFactory


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
        self.hyprshade_system_dir = self.usr_dir / "share/hyprshade/shaders"

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

    def _ensure_mkdir(self):
        for attribute in self.__dict__.values():
            if isinstance(attribute, Path):
                attribute.mkdir(exist_ok=True, parents=True)


@pytest.fixture(autouse=True)
def isolation(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
):
    with Isolation(tmp_path_factory.mktemp("isolation"), monkeypatch) as i:
        yield i


@pytest.fixture()
def _clear_shader_env(shader_dir_env, shader_dir_user, shader_dir_system):
    pass


@pytest.fixture()
def _clear_screen_shader():
    """Clear the current screen shader before and after each test"""

    hyprctl.clear_screen_shader()
    yield
    hyprctl.clear_screen_shader()


@pytest.fixture()
def shader_dir_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    prev_env = os.environ.get(Shader.dirs.ENV_VAR_NAME)

    path = tmp_path / "env/shaders"
    path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, str(path))
    yield path

    if prev_env is None:
        monkeypatch.delenv(Shader.dirs.ENV_VAR_NAME, raising=False)
    else:
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, prev_env)


@pytest.fixture()
def shader_dir_user(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")

    config_path = tmp_path / "config"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_path))

    path = config_path / "hypr/shaders"
    path.mkdir(parents=True, exist_ok=True)
    yield path

    if xdg_config_home is None:
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    else:
        monkeypatch.setenv("XDG_CONFIG_HOME", xdg_config_home)


@pytest.fixture()
def shader_dir_system(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    prev_sysconfig_get_path = sysconfig.get_path

    data_path = tmp_path / "data"
    monkeypatch.setattr(
        sysconfig, "get_path", lambda name: str(data_path) if name == "data" else ""
    )

    path = Path(sysconfig.get_path("data"), "share", "hyprshade", "shaders").resolve()
    path.mkdir(parents=True, exist_ok=True)
    yield path

    monkeypatch.setattr(sysconfig, "get_path", prev_sysconfig_get_path)


def _shader_path_at(name: Path) -> Path:
    path = name / "shader.glsl"
    path.write_text("void main() {}")
    return path


@pytest.fixture()
def shader_path(tmp_path: Path) -> Path:
    return _shader_path_at(tmp_path)


@pytest.fixture()
def shader_path_env(shader_dir_env: Path) -> Path:
    return _shader_path_at(shader_dir_env)


@pytest.fixture()
def shader_path_user(shader_dir_user: Path) -> Path:
    return _shader_path_at(shader_dir_user)


@pytest.fixture()
def shader_path_system(shader_dir_system: Path) -> Path:
    return _shader_path_at(shader_dir_system)


@pytest.fixture()
def shader_path_factory(shader_dir_env: Path) -> ShaderPathFactory:
    def _shader_path(name: str) -> Path:
        path = shader_dir_env / f"{name}.glsl"
        path.write_text("void main() {}")
        return path

    return _shader_path


def pytest_runtest_setup(item: pytest.Item) -> None:
    for marker in item.iter_markers():
        if (
            marker.name == "requires_hyprland"
            and not has_hyprland()
            and not item.config.getoption("--hyprland", default=False)
        ):
            pytest.skip("Not running in hyprland")
        elif marker.name == "requires_pystache" and not has_pystache():
            pytest.skip("pystache not installed")


@lru_cache
def has_hyprland():
    return os.getenv("HYPRLAND_INSTANCE_SIGNATURE") is not None


@lru_cache
def has_pystache() -> bool:
    from importlib.util import find_spec

    return find_spec("pystache") is not None
