import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.shader import hyprctl
from tests.types import ShaderPathFactory

pytestmark = [
    pytest.mark.requires_hyprland(),
]


def test_empty(runner: CliRunner):
    hyprctl.clear_screen_shader()
    result = runner.invoke(cli, ["current"])

    assert result.exit_code == 0
    assert result.output == ""


def test_it(runner: CliRunner, shader_path_factory: ShaderPathFactory):
    shader_path = shader_path_factory("shader1")
    hyprctl.set_screen_shader(str(shader_path))
    result = runner.invoke(cli, ["current"])

    assert result.exit_code == 0
    assert result.output.strip() == "shader1"
