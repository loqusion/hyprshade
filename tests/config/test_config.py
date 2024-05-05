from datetime import time

import pytest

from hyprshade.config.core import Config
from tests.types import ConfigFactory, ShaderPathFactory


def test_example_config(request: pytest.FixtureRequest):
    config = Config(str(request.session.config.rootpath / "examples/config.toml"))
    config.model.parse_fields()

    assert config.model.raw_data == {
        "shaders": [
            {
                "name": "vibrance",
                "start_time": None,
                "end_time": None,
                "default": True,
                "config": None,
            },
            {
                "name": "blue-light-filter",
                "start_time": time(19, 0, 0),
                "end_time": time(6, 0, 0),
                "default": False,
                "config": None,
            },
            {
                "name": "color-filter",
                "start_time": None,
                "end_time": None,
                "default": False,
                "config": {
                    "type": "red-green",
                    "strength": 1.0,
                },
            },
        ]
    }


class TestShaderConfig:
    def test_name(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "config": {"key": 3},
                    }
                ]
            }
        )
        config = config_factory.get_config()

        shader_config = config.shader_config("test")
        assert shader_config is not None
        assert shader_config.name == "test"
        assert shader_config.config == {"key": 3}

    def test_path(
        self, config_factory: ConfigFactory, shader_path_factory: ShaderPathFactory
    ):
        shader_path = shader_path_factory("test")
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "config": {"key": 3},
                    }
                ]
            }
        )
        config = config_factory.get_config()

        shader_config = config.shader_config(str(shader_path))
        assert shader_config is not None
        assert shader_config.name == "test"
        assert shader_config.config == {"key": 3}

    def test_not_found(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "config": {"key": 3},
                    }
                ]
            }
        )
        config = config_factory.get_config()

        shader_config = config.shader_config("not-found")
        assert shader_config is None


class TestShaderVariables:
    def test_name(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "config": {"key": 3},
                    }
                ]
            }
        )
        config = config_factory.get_config()

        shader_variables = config.shader_variables("test")
        assert shader_variables is not None
        assert shader_variables == {"key": 3}

    def test_path(
        self, config_factory: ConfigFactory, shader_path_factory: ShaderPathFactory
    ):
        shader_path = shader_path_factory("test")
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "config": {"key": 3},
                    }
                ]
            }
        )
        config = config_factory.get_config()

        shader_variables = config.shader_variables(str(shader_path))
        assert shader_variables is not None
        assert shader_variables == {"key": 3}

    def test_not_found(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "config": {"key": 3},
                    }
                ]
            }
        )
        config = config_factory.get_config()

        shader_config = config.shader_config("not-found")
        assert shader_config is None


class TestLazyShaderVariables:
    def test_name(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "config": {"key": 3},
                    }
                ]
            }
        )
        config = config_factory.get_config()

        lazy_shader_variables = config.lazy_shader_variables("test")
        shader_variables = lazy_shader_variables()
        assert shader_variables is not None
        assert shader_variables == {"key": 3}

    def test_path(
        self, config_factory: ConfigFactory, shader_path_factory: ShaderPathFactory
    ):
        shader_path = shader_path_factory("test")
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "config": {"key": 3},
                    }
                ]
            }
        )
        config = config_factory.get_config()

        lazy_shader_variables = config.lazy_shader_variables(str(shader_path))
        shader_variables = lazy_shader_variables()
        assert shader_variables is not None
        assert shader_variables == {"key": 3}

    def test_not_found(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "config": {"key": 3},
                    }
                ]
            }
        )
        config = config_factory.get_config()

        shader_config = config.shader_config("not-found")
        assert shader_config is None
