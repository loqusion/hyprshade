import re
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
    pytest.mark.usefixtures("_clear_screen_shader"),
]


@pytest.mark.parametrize("is_long", [False, True])
def test_empty(is_long: bool, runner: CliRunner):
    cmd_args = ["--long"] if is_long else []
    result = runner.invoke(cli, ["ls", *cmd_args])

    assert result.exit_code == 0
    assert result.output == ""


@pytest.mark.parametrize("is_long", [False, True])
def test_single(is_long: bool, runner: CliRunner, shader_path_env: Path):
    cmd_args = ["--long"] if is_long else []
    result = runner.invoke(cli, ["ls", *cmd_args])

    assert result.exit_code == 0

    pattern = "shader" + (
        rf" +{re.escape(shader_path_env.parent.as_posix())}" if is_long else ""
    )
    assert re.match(pattern, result.output.strip()) is not None


@pytest.mark.parametrize("is_long", [False, True])
def test_multiple(
    is_long: bool, runner: CliRunner, shader_path_factory: ShaderPathFactory
):
    shader_names = ["shader1", "shader2", "shader3"]
    shader_paths = list(map(shader_path_factory, shader_names))

    cmd_args = ["--long"] if is_long else []
    result = runner.invoke(cli, ["ls", *cmd_args])

    assert result.exit_code == 0

    for name, path, line in zip(
        shader_names, shader_paths, result.output.strip().splitlines(), strict=True
    ):
        pattern = re.escape(name) + (
            rf" +{re.escape(path.parent.as_posix())}" if is_long else ""
        )
        assert re.match(pattern, line.strip()) is not None


@pytest.mark.parametrize("is_long", [False, True])
@pytest.mark.parametrize("current_index", [0, 1, 2])
def test_active(
    is_long: bool,
    current_index: int,
    runner: CliRunner,
    shader_path_factory: ShaderPathFactory,
):
    shader_names = ["shader1", "shader2", "shader3"]
    shader_paths = list(map(shader_path_factory, shader_names))

    hyprctl.set_screen_shader(shader_paths[current_index].as_posix())
    cmd_args = ["--long"] if is_long else []
    result = runner.invoke(cli, ["ls", *cmd_args])

    assert result.exit_code == 0

    for i, (name, path, line) in enumerate(
        zip(shader_names, shader_paths, result.output.strip().splitlines(), strict=True)
    ):
        pattern = (
            (re.escape("* ") if i == current_index else "")
            + re.escape(name)
            + (rf" +{re.escape(path.parent.as_posix())}" if is_long else "")
        )
        assert re.match(pattern, line.strip()) is not None
