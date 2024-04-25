import pytest

from hyprshade.cli.utils import ContextObject
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
