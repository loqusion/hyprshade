from pathlib import Path

import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.shader import hyprctl

pytestmark = [
    pytest.mark.requires_hyprland(),
    pytest.mark.usefixtures("_save_screen_shader"),
]


def test_off(runner: CliRunner):
    result = runner.invoke(cli, "off")

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() is None


def test_off_after_set(runner: CliRunner, shader_path_env: Path):
    hyprctl.set_screen_shader(shader_path_env.as_posix())
    result = runner.invoke(cli, "off")

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() is None
