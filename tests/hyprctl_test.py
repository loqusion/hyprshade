from pathlib import Path

import pytest

from hyprshade import hyprctl


@pytest.fixture()
def shader_path(tmp_path: Path):
    shader_path = tmp_path / "shader.frag"
    shader_path.write_text("void main() {}")
    return shader_path


@pytest.mark.hyprland()
@pytest.mark.usefixtures("_save_screen_shader")
class TestHyprctl:
    def test_hyprctl(self, shader_path: Path):
        hyprctl.set_screen_shader(str(shader_path))
        assert hyprctl.get_screen_shader() == str(shader_path)

    def test_clear(self):
        hyprctl.clear_screen_shader()
        assert hyprctl.get_screen_shader() is None
