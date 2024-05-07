from pathlib import Path

import pytest
from click.testing import CliRunner
from syrupy.assertion import SnapshotAssertion

from hyprshade.cli import cli
from hyprshade.shader import hyprctl
from hyprshade.shader.core import Shader
from tests.types import ConfigFactory, ShaderPathFactory

pytestmark = [
    pytest.mark.requires_hyprland(),
]


def test_path(runner: CliRunner, shader_path: Path):
    result = runner.invoke(cli, ["on", shader_path.as_posix()])

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() == shader_path.as_posix()


def test_name(runner: CliRunner, shader_path_factory: ShaderPathFactory):
    shader_path = shader_path_factory("shader")
    result = runner.invoke(cli, ["on", "shader"])

    assert result.exit_code == 0
    assert hyprctl.get_screen_shader() == shader_path.as_posix()


def test_no_args(runner: CliRunner):
    initial_shader = hyprctl.get_screen_shader()
    result = runner.invoke(cli, ["on"])

    assert result.exit_code != 0
    assert result.exception is not None
    assert "missing argument" in result.stderr.lower()
    assert hyprctl.get_screen_shader() == initial_shader


def test_invalid_shader(runner: CliRunner):
    initial_shader = hyprctl.get_screen_shader()
    result = runner.invoke(cli, ["on", "invalid"])

    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
    assert hyprctl.get_screen_shader() == initial_shader


def test_invalid_shader_dot(runner: CliRunner, shader_path_factory: ShaderPathFactory):
    initial_shader = hyprctl.get_screen_shader()
    _shader_path = shader_path_factory("invalid.name")
    result = runner.invoke(cli, ["on", "invalid.name"])

    assert result.exit_code != 0
    assert isinstance(result.exception, ValueError)
    assert hyprctl.get_screen_shader() == initial_shader


class TestVarOption:
    def test(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
        snapshot: SnapshotAssertion,
    ):
        shader_path_factory(
            "shader",
            extension="glsl.mustache",
            text=("""const int key = {{key}};\n""" """void main() {}"""),
        )
        result = runner.invoke(cli, ["on", "shader", "--var", "key=3"])

        assert result.exit_code == 0
        current_shader_path = hyprctl.get_screen_shader()
        assert current_shader_path is not None
        assert (
            Shader._get_template_instance_content_without_metadata(current_shader_path)
            == snapshot
        )

    def test_multiple(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
        snapshot: SnapshotAssertion,
    ):
        shader_path_factory(
            "shader",
            extension="glsl.mustache",
            text=(
                """const int WORLD = {{world}};\n"""
                """const int key = {{key}};\n"""
                """void main() {}"""
            ),
        )
        result = runner.invoke(
            cli, ["on", "shader", "--var", "key=world", "--var", "world=5"]
        )

        assert result.exit_code == 0
        current_shader_path = hyprctl.get_screen_shader()
        assert current_shader_path is not None
        assert (
            Shader._get_template_instance_content_without_metadata(current_shader_path)
            == snapshot
        )

    def test_dot(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
        snapshot: SnapshotAssertion,
    ):
        shader_path_factory(
            "shader",
            extension="glsl.mustache",
            text=("""const int bar = {{foo.bar}};\n""" """void main() {}"""),
        )
        result = runner.invoke(cli, ["on", "shader", "--var", "foo.bar=3"])

        assert result.exit_code == 0
        current_shader_path = hyprctl.get_screen_shader()
        assert current_shader_path is not None
        assert (
            Shader._get_template_instance_content_without_metadata(current_shader_path)
            == snapshot
        )

    def test_dot_shallow_merge(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
        snapshot: SnapshotAssertion,
    ):
        shader_path_factory(
            "shader",
            extension="glsl.mustache",
            text=(
                """const int bar = {{foo.bar}};\n"""
                """const int baz = {{foo.baz}};\n"""
                """const int qux = {{foo.qux}};\n"""
                """void main() {}"""
            ),
        )
        result = runner.invoke(
            cli,
            [
                "on",
                "shader",
                "--var",
                "foo.bar=1",
                "--var",
                "foo.baz=2",
                "--var",
                "foo.qux=3",
            ],
        )

        assert result.exit_code == 0
        current_shader_path = hyprctl.get_screen_shader()
        assert current_shader_path is not None
        assert (
            Shader._get_template_instance_content_without_metadata(current_shader_path)
            == snapshot
        )

    def test_dot_deep_merge(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
        snapshot: SnapshotAssertion,
    ):
        shader_path_factory(
            "shader",
            extension="glsl.mustache",
            text=(
                """const int bar = {{foo.bar}};\n"""
                """const int baz_qux = {{foo.baz.qux}};\n"""
                """const int baz_baz_qux = {{foo.baz.baz.qux}};\n"""
                """void main() {}"""
            ),
        )
        result = runner.invoke(
            cli,
            [
                "on",
                "shader",
                "--var",
                "foo.bar=1",
                "--var",
                "foo.baz.qux=2",
                "--var",
                "foo.baz.baz.qux=3",
            ],
        )

        assert result.exit_code == 0
        current_shader_path = hyprctl.get_screen_shader()
        assert current_shader_path is not None
        assert (
            Shader._get_template_instance_content_without_metadata(current_shader_path)
            == snapshot
        )

    def test_override(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
        snapshot: SnapshotAssertion,
    ):
        shader_path_factory(
            "shader",
            extension="glsl.mustache",
            text=(
                """const int WORLD = {{world}};\n"""
                """const int key = {{key}};\n"""
                """void main() {}"""
            ),
        )
        result = runner.invoke(
            cli,
            [
                "on",
                "shader",
                "--var",
                "key=planet",
                "--var",
                "key=world",
                "--var",
                "world=5",
            ],
        )

        assert result.exit_code == 0
        current_shader_path = hyprctl.get_screen_shader()
        assert current_shader_path is not None
        assert (
            Shader._get_template_instance_content_without_metadata(current_shader_path)
            == snapshot
        )

    def test_override_deep(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
        snapshot: SnapshotAssertion,
    ):
        shader_path_factory(
            "shader",
            extension="glsl.mustache",
            text=(
                """const int foo_bar_baz = {{foo.bar.baz}};\n""" """void main() {}"""
            ),
        )
        result = runner.invoke(
            cli,
            [
                "on",
                "shader",
                "--var",
                "foo.bar=0",
                "--var",
                "foo.bar.baz=1",
            ],
        )

        assert result.exit_code == 0
        current_shader_path = hyprctl.get_screen_shader()
        assert current_shader_path is not None
        assert (
            Shader._get_template_instance_content_without_metadata(current_shader_path)
            == snapshot
        )

    def test_override_from_deep(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
        snapshot: SnapshotAssertion,
    ):
        shader_path_factory(
            "shader",
            extension="glsl.mustache",
            text=("""const int foo_bar = {{foo.bar}};\n""" """void main() {}"""),
        )
        result = runner.invoke(
            cli,
            [
                "on",
                "shader",
                "--var",
                "foo.bar.baz=0",
                "--var",
                "foo.bar=1",
            ],
        )

        assert result.exit_code == 0
        current_shader_path = hyprctl.get_screen_shader()
        assert current_shader_path is not None
        assert (
            Shader._get_template_instance_content_without_metadata(current_shader_path)
            == snapshot
        )

    def test_merge_with_config(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
        config_factory: ConfigFactory,
        snapshot: SnapshotAssertion,
    ):
        shader_path_factory(
            "shader",
            extension="glsl.mustache",
            text=(
                """const int r = {{balance.r}};\n"""
                """const int g = {{balance.g}};\n"""
                """const int b = {{balance.b}};\n"""
                """void main() {}"""
            ),
        )
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "shader",
                        "config": {"balance": {"r": 1, "g": 5}},
                    }
                ]
            }
        )
        result = runner.invoke(
            cli,
            [
                "on",
                "shader",
                "--var",
                "balance.g=2",
                "--var",
                "balance.b=3",
            ],
        )

        assert result.exit_code == 0
        current_shader_path = hyprctl.get_screen_shader()
        assert current_shader_path is not None
        assert (
            Shader._get_template_instance_content_without_metadata(current_shader_path)
            == snapshot
        )

    def test_no_equals(
        self,
        runner: CliRunner,
        shader_path_factory: ShaderPathFactory,
    ):
        shader_path_factory(
            "shader", extension="glsl.mustache", text="""void main() {}"""
        )
        result = runner.invoke(cli, ["on", "shader", "--var", "key"])

        assert result.exit_code != 0
        assert "Invalid value for '--var' / '-V'" in result.stderr
