import re
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.shader import hyprctl

pytestmark = [
    pytest.mark.requires_hyprland(),
    pytest.mark.usefixtures("_save_screen_shader"),
    pytest.mark.usefixtures("_clear_shader_env"),
    pytest.mark.usefixtures("_clear_screen_shader"),
]


class TestLs:
    def test_empty(self, runner: CliRunner):
        result = runner.invoke(cli, ["ls"])

        assert result.exit_code == 0
        assert result.output == ""

    def test_single(self, runner: CliRunner, shader_path_env: Path):
        result = runner.invoke(cli, ["ls"])

        assert result.exit_code == 0
        assert result.output.strip() == "shader"

    def test_multiple(
        self, runner: CliRunner, shader_path_factory: Callable[[str], Path]
    ):
        shader_path_factory("shader1")
        shader_path_factory("shader2")
        shader_path_factory("shader3")

        result = runner.invoke(cli, ["ls"])

        assert result.exit_code == 0
        line = iter(result.output.strip().splitlines())
        assert next(line).strip() == "shader1"
        assert next(line).strip() == "shader2"
        assert next(line).strip() == "shader3"
        assert next(line, None) is None

    def test_active(
        self, runner: CliRunner, shader_path_factory: Callable[[str], Path]
    ):
        shader_path_factory("shader1")
        shader2_path = shader_path_factory("shader2")
        shader_path_factory("shader3")

        hyprctl.set_screen_shader(shader2_path.as_posix())
        result = runner.invoke(cli, ["ls"])

        assert result.exit_code == 0
        line = iter(result.output.strip().splitlines())
        assert next(line).strip() == "shader1"
        assert next(line).strip() == "* shader2"
        assert next(line).strip() == "shader3"
        assert next(line, None) is None


class TestLsLong:
    def test_empty(self, runner: CliRunner):
        result = runner.invoke(cli, ["ls", "--long"])

        assert result.exit_code == 0
        assert result.output == ""

    def test_single(self, runner: CliRunner, shader_path_env: Path):
        result = runner.invoke(cli, ["ls", "--long"])

        assert result.exit_code == 0

        pattern = rf"shader +{re.escape(shader_path_env.parent.as_posix())}"
        assert re.match(pattern, result.output.strip()) is not None

    def test_multiple(
        self, runner: CliRunner, shader_path_factory: Callable[[str], Path]
    ):
        shader1_path = shader_path_factory("shader1")
        shader2_path = shader_path_factory("shader2")
        shader3_path = shader_path_factory("shader3")

        result = runner.invoke(cli, ["ls", "--long"])

        assert result.exit_code == 0
        line = iter(result.output.strip().splitlines())

        pattern = rf"shader1 +{re.escape(shader1_path.parent.as_posix())}"
        assert re.match(pattern, next(line).strip()) is not None

        pattern = rf"shader2 +{re.escape(shader2_path.parent.as_posix())}"
        assert re.match(pattern, next(line).strip()) is not None

        pattern = rf"shader3 +{re.escape(shader3_path.parent.as_posix())}"
        assert re.match(pattern, next(line).strip()) is not None

        assert next(line, None) is None

    def test_active(
        self, runner: CliRunner, shader_path_factory: Callable[[str], Path]
    ):
        shader1_path = shader_path_factory("shader1")
        shader2_path = shader_path_factory("shader2")
        shader3_path = shader_path_factory("shader3")

        hyprctl.set_screen_shader(shader2_path.as_posix())
        result = runner.invoke(cli, ["ls", "--long"])

        assert result.exit_code == 0
        line = iter(result.output.strip().splitlines())

        pattern = rf"shader1 +{re.escape(shader1_path.parent.as_posix())}"
        assert re.match(pattern, next(line).strip()) is not None

        pattern = rf"\* shader2 +{re.escape(shader2_path.parent.as_posix())}"
        assert re.match(pattern, next(line).strip()) is not None

        pattern = rf"shader3 +{re.escape(shader3_path.parent.as_posix())}"
        assert re.match(pattern, next(line).strip()) is not None

        assert next(line, None) is None
