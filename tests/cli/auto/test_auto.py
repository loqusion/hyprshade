from datetime import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.shader import hyprctl
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
        ("12:00:00", False),
        ("19:59:30", False),
        ("20:00:00", True),
        ("20:30:00", True),
        ("20:59:30", True),
        ("21:00:00", False),
        ("23:00:00", False),
    ],
)
@pytest.mark.parametrize("with_default", [False, True])
def test_scheduled(
    time_str: str,
    expected: bool,
    with_default: bool,
    runner: CliRunner,
    shader_path_factory: ShaderPathFactory,
    config_factory: ConfigFactory,
):
    initial_shader_path = shader_path_factory("initial")
    scheduled_shader_path = shader_path_factory("scheduled")
    default_shader_path = shader_path_factory("default")
    hyprctl.set_screen_shader(initial_shader_path.as_posix())

    config_dict = {
        "shaders": [
            {
                "name": "scheduled",
                "start_time": time.fromisoformat("20:00"),
                "end_time": time.fromisoformat("21:00"),
            },
        ]
    }
    if with_default:
        config_dict["shaders"].append({"name": "default", "default": True})
    config_factory.write(config_dict)

    with freeze_time(time_str):
        result = runner.invoke(cli, ["auto"])

        if expected:
            assert result.exit_code == 0
            assert hyprctl.get_screen_shader() == scheduled_shader_path.as_posix()
        elif with_default:
            assert result.exit_code == 0
            assert hyprctl.get_screen_shader() == default_shader_path.as_posix()
        else:
            assert result.exit_code == 0
            assert hyprctl.get_screen_shader() is None


def test_no_config(runner: CliRunner):
    result = runner.invoke(cli, ["auto"])

    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
