from collections.abc import Sequence

import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.shader import hyprctl
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
