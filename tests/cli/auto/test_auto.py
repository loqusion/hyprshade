from datetime import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.shader import hyprctl
from hyprshade.shader.core import Shader
from tests.helpers import freeze_time
from tests.types import ConfigFactory, ShaderPathFactory

pytestmark = [
    pytest.mark.requires_hyprland,
]


def test_none(runner: CliRunner, shader_path: Path, config_factory: ConfigFactory):
    config_factory.write({})
    hyprctl.set_screen_shader(shader_path.as_posix())
    result = runner.invoke(cli, ["auto"])

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() is None


def test_default(
    runner: CliRunner,
    shader_path_factory: ShaderPathFactory,
    config_factory: ConfigFactory,
):
    initial_shader_path = shader_path_factory("initial")
    default_shader_path = shader_path_factory("default")
    hyprctl.set_screen_shader(initial_shader_path.as_posix())

    config_factory.write({"shaders": [{"name": "default", "default": True}]})

    result = runner.invoke(cli, ["auto"])

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() == default_shader_path.as_posix()


@pytest.mark.parametrize(
    ("time_str", "expected"),
    [
        ("00:00:00", "default"),
        ("12:00:00", "default"),
        ("19:59:30", "default"),
        ("20:00:00", "test1"),
        ("20:30:00", "test1"),
        ("20:59:30", "test1"),
        ("21:00:00", "test2"),
        ("22:00:00", "test2"),
        ("22:59:30", "test2"),
        ("23:00:00", "test3"),
        ("23:30:00", "test3"),
        ("23:59:30", "test3"),
    ],
)
def test_scheduled(
    time_str: str,
    expected: str,
    runner: CliRunner,
    shader_path_factory: ShaderPathFactory,
    config_factory: ConfigFactory,
):
    initial_shader_path = shader_path_factory("initial")
    shader_path_factory("test1")
    shader_path_factory("test2")
    shader_path_factory("test3")
    shader_path_factory("default")
    hyprctl.set_screen_shader(initial_shader_path.as_posix())

    config_dict = {
        "shaders": [
            {
                "name": "test1",
                "start_time": time.fromisoformat("20:00"),
                "end_time": time.fromisoformat("21:00"),
            },
            {
                "name": "test2",
                "start_time": time.fromisoformat("21:00"),
            },
            {
                "name": "test3",
                "start_time": time.fromisoformat("23:00"),
                "end_time": time.fromisoformat("00:00"),
            },
            {
                "name": "default",
                "default": True,
            },
        ]
    }
    config_factory.write(config_dict)

    with freeze_time(time_str):
        result = runner.invoke(cli, ["auto"])

        assert result.exit_code == 0
        current_screen_shader_path = hyprctl.get_screen_shader()
        assert current_screen_shader_path is not None
        assert Shader.path_to_name(current_screen_shader_path) == expected


def test_no_config(runner: CliRunner):
    result = runner.invoke(cli, ["auto"])

    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
