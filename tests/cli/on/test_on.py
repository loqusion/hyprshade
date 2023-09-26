from pathlib import Path

import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.shader import hyprctl

pytestmark = [
    pytest.mark.requires_hyprland(),
    pytest.mark.usefixtures("_save_screen_shader"),
]


def test_path(runner: CliRunner, shader_path_env: Path):
    result = runner.invoke(cli, ["on", shader_path_env.as_posix()])

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() == shader_path_env.as_posix()


def test_name(runner: CliRunner, shader_path_env: Path):
    result = runner.invoke(cli, ["on", "shader"])

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() == shader_path_env.as_posix()


def test_no_args(runner: CliRunner):
    initial_shader = hyprctl.get_screen_shader()
    result = runner.invoke(cli, ["on"])

    assert result.exit_code != 0
    assert result.exception is not None
    assert "missing argument" in result.output.lower()
    assert hyprctl.get_screen_shader() == initial_shader


def test_invalid_shader(
    runner: CliRunner,
    shader_dir_env: Path,
    shader_dir_user: Path,
    shader_dir_system: Path,
):
    initial_shader = hyprctl.get_screen_shader()
    result = runner.invoke(cli, ["on", "invalid"])

    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
    assert hyprctl.get_screen_shader() == initial_shader
