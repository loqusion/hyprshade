from pathlib import Path

import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.shader import hyprctl
from tests.types import ShaderPathFactory

pytestmark = [
    pytest.mark.requires_hyprland(),
    pytest.mark.usefixtures("_save_screen_shader"),
    pytest.mark.usefixtures("_clear_shader_env"),
]


class TestCurrent:
    def test_empty(self, runner: CliRunner, shader_path_env: Path):
        hyprctl.clear_screen_shader()

        result = runner.invoke(cli, ["current"])

        assert result.exit_code == 0
        assert result.output == ""

    def test_it(self, runner: CliRunner, shader_path_factory: ShaderPathFactory):
        shader_path_factory("shader1")

        hyprctl.set_screen_shader("shader1")

        result = runner.invoke(cli, ["current"])

        assert result.exit_code == 0
        assert result.output.strip() == "shader1"
