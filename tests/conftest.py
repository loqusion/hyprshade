from pathlib import Path

import pytest

from hyprshade import hyprctl


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
