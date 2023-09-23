import os
from functools import lru_cache
from pathlib import Path

import pytest

from hyprshade.shader import hyprctl


@pytest.fixture(scope="module")
def _save_screen_shader():
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


@pytest.fixture()
def shader_path(tmp_path: Path):
    shader_path = tmp_path / "shader.frag"
    shader_path.write_text("void main() {}")
    return shader_path


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
