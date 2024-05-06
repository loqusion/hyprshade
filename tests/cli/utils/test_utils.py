import pytest

from hyprshade.cli.utils import ContextObject, VarOptionPair
from tests.types import ConfigFactory


class TestContextObject:
    def test_get_config(self, config_factory: ConfigFactory):
        config_factory.write({})
        config = config_factory.get_config()
        obj = ContextObject(config)

        assert obj.get_config(raising=True) is config

    def test_get_config_none(self):
        obj = ContextObject(None)

        assert obj.get_config(raising=False) is None
        with pytest.raises(FileNotFoundError):
            obj.get_config(raising=True)


class TestConvertValue:
    def test(self):
        assert VarOptionPair.convert_value("1") == 1
        assert VarOptionPair.convert_value("-1") == -1
        assert VarOptionPair.convert_value("036") == 36

        assert VarOptionPair.convert_value("3.5") == 3.5
        assert VarOptionPair.convert_value("-4.93") == -4.93

        assert VarOptionPair.convert_value("4.0.0") == "4.0.0"
        assert VarOptionPair.convert_value("-4.0.0") == "-4.0.0"

        assert VarOptionPair.convert_value("0x36") == "0x36"
        assert VarOptionPair.convert_value("3b") == "3b"

        assert VarOptionPair.convert_value("foo") == "foo"
