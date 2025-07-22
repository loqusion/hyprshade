import os
import sysconfig
from functools import lru_cache
from pathlib import Path

import pytest

from hyprshade.shader import Shader, hyprctl
from tests.types import ShaderPathFactory


@pytest.fixture(scope="module")
def _save_screen_shader():
    """Save the current screen shader and restore it after testing"""

    screen_shader = hyprctl.get_screen_shader()
    yield

    if screen_shader is None:
        hyprctl.clear_screen_shader()
        return
    try:
        hyprctl.set_screen_shader(screen_shader)
    except BaseException:
        import os

        hyprctl.clear_screen_shader()
        os.system('notify-send "hyprshade" "Failed to restore screen shader"')


@pytest.fixture
def _clear_shader_env(shader_dir_env, shader_dir_user, shader_dir_system):
    pass


@pytest.fixture
def _clear_screen_shader():
    """Clear the current screen shader before and after each test"""

    hyprctl.clear_screen_shader()
    yield
    hyprctl.clear_screen_shader()


@pytest.fixture
def shader_dir_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    prev_env = os.environ.get(Shader.dirs.ENV_VAR_NAME)

    path_ = tmp_path / "env/shaders"
    path_.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, str(path_))
    yield path_

    if prev_env is None:
        monkeypatch.delenv(Shader.dirs.ENV_VAR_NAME, raising=False)
    else:
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, prev_env)


@pytest.fixture
def shader_dir_user(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")

    config_path = tmp_path / "config"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_path))

    path_ = config_path / "hypr/shaders"
    path_.mkdir(parents=True, exist_ok=True)
    yield path_

    if xdg_config_home is None:
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    else:
        monkeypatch.setenv("XDG_CONFIG_HOME", xdg_config_home)


@pytest.fixture
def shader_dir_system(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    prev_sysconfig_get_path = sysconfig.get_path

    data_path = tmp_path / "data"
    monkeypatch.setattr(
        sysconfig, "get_path", lambda name: str(data_path) if name == "data" else ""
    )

    path_ = Path(sysconfig.get_path("data"), "share", "hyprshade", "shaders").resolve()
    path_.mkdir(parents=True, exist_ok=True)
    yield path_

    monkeypatch.setattr(sysconfig, "get_path", prev_sysconfig_get_path)


def _shader_path_at(dir_: Path) -> Path:
    path_ = dir_ / "shader.glsl"
    path_.write_text("void main() {}")
    return path_


@pytest.fixture
def shader_path(tmp_path: Path) -> Path:
    return _shader_path_at(tmp_path)


@pytest.fixture
def shader_path_env(shader_dir_env: Path) -> Path:
    return _shader_path_at(shader_dir_env)


@pytest.fixture
def shader_path_user(shader_dir_user: Path) -> Path:
    return _shader_path_at(shader_dir_user)


@pytest.fixture
def shader_path_system(shader_dir_system: Path) -> Path:
    return _shader_path_at(shader_dir_system)


@pytest.fixture
def shader_path_factory(shader_dir_env: Path) -> ShaderPathFactory:
    def _shader_path(name: str) -> Path:
        path_ = shader_dir_env / f"{name}.glsl"
        path_.write_text("void main() {}")
        return path_

    return _shader_path


def pytest_runtest_setup(item: pytest.Item) -> None:
    for marker in item.iter_markers():
        if (
            marker.name == "requires_hyprland"
            and not has_hyprland()
            and not item.config.getoption("--hyprland", default=False)
        ):
            pytest.skip("Not running in hyprland")


@lru_cache
def has_hyprland():
    return os.getenv("HYPRLAND_INSTANCE_SIGNATURE") is not None
