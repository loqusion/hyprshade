from pathlib import Path

import pytest

from hyprshade.shader import hyprctl

pytestmark = [
    pytest.mark.requires_hyprland(),
    pytest.mark.usefixtures("_save_screen_shader"),
]


def test_hyprctl(shader_path: Path):
    hyprctl.set_screen_shader(str(shader_path))
    assert hyprctl.get_screen_shader() == str(shader_path)


def test_clear():
    hyprctl.clear_screen_shader()
    assert hyprctl.get_screen_shader() is None
