import contextlib
import os
import sysconfig
from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

import pytest

from hyprshade.shader import hyprctl
from hyprshade.shader.core import Shader
from tests.types import ShaderPathFactory


@pytest.fixture(scope="session", autouse=True)
def _save_and_restore_shader():
    with contextlib.suppress(hyprctl.HyprctlError, FileNotFoundError):
        screen_shader = hyprctl.get_screen_shader()

    yield

    with contextlib.suppress(hyprctl.HyprctlError, FileNotFoundError):
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


@pytest.fixture(scope="session", autouse=True)
def isolation():
    with temp_directory() as d:
        state_dir = d / "state"
        state_dir.mkdir()
        config_dir = d / "config"
        config_dir.mkdir()

        env = {
            "XDG_CONFIG_HOME": str(config_dir),
            "XDG_STATE_HOME": str(state_dir),
        }

        with as_cwd(d), EnvVars(env):
            yield d


@contextmanager
def temp_directory() -> Generator[Path, None, None]:
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as d:
        yield Path(d).resolve()


@contextmanager
def as_cwd(path: Path) -> Generator[Path, None, None]:
    old_cwd = os.getcwd()
    os.chdir(path)

    yield path

    os.chdir(old_cwd)


class EnvVars(dict):
    def __init__(self, env: dict):
        super().__init__(os.environ)
        self.old_env = dict(self)

        self.update(env)

    def __enter__(self):
        os.environ.clear()
        os.environ.update(self)

    def __exit__(self, *exc):
        os.environ.clear()
        os.environ.update(self.old_env)


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
