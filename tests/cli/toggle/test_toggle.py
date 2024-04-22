from collections.abc import Sequence
from datetime import time

import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.shader import hyprctl
from hyprshade.shader.core import Shader
from tests.helpers import freeze_time
from tests.types import ConfigFactory, ShaderPathFactory

pytestmark = [
    pytest.mark.requires_hyprland(),
]


@pytest.mark.parametrize(
    "extra_args",
    [
        [],
        ["--fallback", "bar"],
        ["--fallback-default"],
        ["--fallback-auto"],
    ],
)
def test_toggles_on(
    extra_args: Sequence[str],
    runner: CliRunner,
    shader_path_factory: ShaderPathFactory,
    config_factory: ConfigFactory,
):
    config_factory.write({})
    initial_shader_path = shader_path_factory("initial")
    shader_path = shader_path_factory("foo")
    hyprctl.set_screen_shader(str(initial_shader_path))

    result = runner.invoke(cli, ["toggle", "foo", *extra_args])

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() == str(shader_path)


def test_toggles_off(
    runner: CliRunner,
    shader_path_factory: ShaderPathFactory,
):
    initial_shader_path = shader_path_factory("initial")
    hyprctl.set_screen_shader(str(initial_shader_path))

    result = runner.invoke(cli, ["toggle", "initial"])

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() is None


def test_fallback(runner: CliRunner, shader_path_factory: ShaderPathFactory):
    initial_shader_path = shader_path_factory("initial")
    shader_path = shader_path_factory("foo")
    hyprctl.set_screen_shader(str(initial_shader_path))

    result = runner.invoke(cli, ["toggle", "initial", "--fallback", "foo"])

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() == str(shader_path)


@pytest.mark.parametrize("is_default_in_config", [False, True])
def test_fallback_default(
    is_default_in_config: bool,
    runner: CliRunner,
    shader_path_factory: ShaderPathFactory,
    config_factory: ConfigFactory,
):
    if is_default_in_config:
        config_factory.write({"shaders": [{"name": "default", "default": True}]})
    else:
        config_factory.write({"shaders": []})
    initial_shader_path = shader_path_factory("initial")
    default_shader_path = shader_path_factory("default")
    hyprctl.set_screen_shader(str(initial_shader_path))

    result = runner.invoke(cli, ["toggle", "initial", "--fallback-default"])

    assert result.exit_code == 0
    if is_default_in_config:
        assert hyprctl.get_screen_shader() == str(default_shader_path)
    else:
        assert hyprctl.get_screen_shader() is None


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
def test_fallback_auto(
    time_str: str,
    expected: str,
    runner: CliRunner,
    shader_path_factory: ShaderPathFactory,
    config_factory: ConfigFactory,
):
    config_factory.write(
        {
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
    )
    shader_path_factory("test1")
    shader_path_factory("test2")
    shader_path_factory("test3")
    shader_path_factory("default")
    initial_shader_path = shader_path_factory("initial")
    hyprctl.set_screen_shader(str(initial_shader_path))

    with freeze_time(time_str):
        result = runner.invoke(cli, ["toggle", "initial", "--fallback-auto"])

        assert result.exit_code == 0
        current_screen_shader_path = hyprctl.get_screen_shader()
        assert current_screen_shader_path is not None
        assert Shader.path_to_name(current_screen_shader_path) == expected


def test_no_config_no_positional_argument(runner: CliRunner):
    result = runner.invoke(cli, ["toggle"])

    assert result.exit_code != 0
    assert "requires a config file" in str(result.exception)


def test_no_config_fallback_default(
    runner: CliRunner, shader_path_factory: ShaderPathFactory
):
    shader_path_factory("foo")
    result = runner.invoke(cli, ["toggle", "--fallback-default", "foo"])

    assert result.exit_code != 0
    assert "--fallback-default" in str(result.exception)
    assert "requires a config file" in str(result.exception)


def test_no_config_fallback_auto(
    runner: CliRunner, shader_path_factory: ShaderPathFactory
):
    shader_path_factory("foo")
    result = runner.invoke(cli, ["toggle", "--fallback-auto", "foo"])

    assert result.exit_code != 0
    assert "--fallback-auto" in str(result.exception)
    assert "requires a config file" in str(result.exception)


@pytest.mark.parametrize(
    "extra_args",
    [
        ["--fallback", "bar", "--fallback-default"],
        ["--fallback", "bar", "--fallback-auto"],
        ["--fallback-default", "--fallback-auto"],
        ["--fallback", "bar", "--fallback-default", "--fallback-auto"],
    ],
)
def test_multiple_fallback_options(
    extra_args: Sequence[str], runner: CliRunner, shader_path_factory: ShaderPathFactory
):
    shader_path_factory("foo")
    result = runner.invoke(cli, ["toggle", "foo", *extra_args])

    assert result.exit_code != 0
    assert "--fallback" in result.stderr or "--fallback" in str(result.exception)
