from datetime import time

import pytest
from more_itertools import quantify

from hyprshade.config.model import ConfigError, RootConfig


class _RootConfig(RootConfig):
    def __init__(self, config_dict: dict, *, path: str = "", steps: tuple = ()):
        super().__init__(config_dict, path=path, steps=steps)


def test_default():
    config = _RootConfig({})
    config.parse_fields()

    assert config.raw_data == {"shaders": []}


class TestBackwardsCompatibility:
    def test_shades(self):
        config = _RootConfig({"shades": [{"name": "foo"}]})

        assert config.shaders[0].name == "foo"

    def test_shades_not_array(self):
        config = _RootConfig({"shades": 9000})

        with pytest.raises(ConfigError, match="must be an array"):
            _ = config.shaders

    def test_shades_merges_with_shaders(self):
        config = _RootConfig(
            {
                "shaders": [{"name": "foo"}],
                "shades": [{"name": "bar"}],
            }
        )

        assert quantify(config.shaders, pred=lambda s: s.name == "foo") == 1
        assert quantify(config.shaders, pred=lambda s: s.name == "bar") == 1


class TestShaders:
    def test_default(self):
        config = _RootConfig({})

        assert config.shaders == config.shaders == []

    def test_not_array(self):
        config = _RootConfig({"shaders": 9000})

        with pytest.raises(ConfigError, match="must be an array"):
            _ = config.shaders


class TestShadersItems:
    def test_not_dict(self):
        config = _RootConfig({"shaders": [9000]})

        with pytest.raises(ConfigError, match="must be a table"):
            _ = config.shaders

    def test_start_time_and_default(self):
        config = _RootConfig(
            {"shaders": [{"start_time": time(12, 0, 0), "default": True}]}
        )

        with pytest.raises(
            ConfigError, match="Default shader must not define `start_time`"
        ):
            _ = config.shaders

    def test_start_time_equals_end_time(self):
        config = _RootConfig(
            {"shaders": [{"start_time": time(12, 0, 0), "end_time": time(12, 0, 0)}]}
        )
        with pytest.raises(ConfigError, match="must not be the same"):
            _ = config.shaders

    def test_multiple_default(self):
        config = _RootConfig(
            {
                "shaders": [
                    {"name": "foo", "default": True},
                    {"name": "bar", "default": True},
                ]
            }
        )

        with pytest.raises(ConfigError, match="Only one default shader is allowed"):
            _ = config.shaders


class TestShadersName:
    def test_string(self):
        config = _RootConfig({"shaders": [{"name": "foo"}]})

        assert config.shaders[0].name == "foo"

    def test_required(self):
        config = _RootConfig({"shaders": [{}]})

        with pytest.raises(ConfigError, match="required"):
            _ = config.shaders[0].name

    def test_not_string(self):
        config = _RootConfig({"shaders": [{"name": 9000}]})

        with pytest.raises(ConfigError, match="must be a string"):
            _ = config.shaders[0].name

    def test_contains_period(self):
        config = _RootConfig({"shaders": [{"name": "foo.bar"}]})

        with pytest.raises(ConfigError, match="must not contain a period"):
            _ = config.shaders[0].name


class TestShadersStartTimeAndEndTime:
    @pytest.mark.parametrize("field", ["start_time", "end_time"])
    def test_default(self, field: str):
        config = _RootConfig({"shaders": [{"name": "foo"}]})

        assert getattr(config.shaders[0], field) is None

    @pytest.mark.parametrize("field", ["start_time", "end_time"])
    def test_time(self, field: str):
        config = _RootConfig({"shaders": [{"name": "foo", field: time(12, 0, 0)}]})

        assert getattr(config.shaders[0], field) == time(12, 0, 0)

    @pytest.mark.parametrize("field", ["start_time", "end_time"])
    def test_not_time(self, field: str):
        config = _RootConfig({"shaders": [{"name": "foo", field: 9000}]})

        with pytest.raises(ConfigError, match="must be time"):
            _ = getattr(config.shaders[0], field)


class TestShadersDefault:
    def test_default(self):
        config = _RootConfig({"shaders": [{"name": "foo"}]})

        assert config.shaders[0].default is False

    def test_bool(self):
        config = _RootConfig({"shaders": [{"name": "foo", "default": True}]})

        assert config.shaders[0].default is True

    def test_not_bool(self):
        config = _RootConfig({"shaders": [{"name": "foo", "default": 9000}]})

        with pytest.raises(ConfigError, match="must be a boolean"):
            _ = config.shaders[0].default


class TestShadersConfig:
    def test_default(self):
        config = _RootConfig({"shaders": [{"name": "foo"}]})
        assert config.shaders[0].config is None

    def test_dict(self):
        config = _RootConfig({"shaders": [{"name": "foo", "config": {"foo": "bar"}}]})

        assert config.shaders[0].config == {"foo": "BAR"}

    def test_not_dict(self):
        config = _RootConfig({"shaders": [{"name": "foo", "config": 9000}]})

        with pytest.raises(ConfigError, match="must be a table"):
            _ = config.shaders[0].config

    def test_key_not_string(self):
        config = _RootConfig({"shaders": [{"name": "foo", "config": {9000: "bar"}}]})

        with pytest.raises(ConfigError, match="must be a string"):
            _ = config.shaders[0].config
