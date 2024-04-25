import pytest

from hyprshade.cli.utils import ContextObject, write_systemd_user_unit
from tests.conftest import Isolation
from tests.types import ConfigFactory


def test_write_systemd_user_unit(isolation: Isolation):
    write_systemd_user_unit("service", "foo")
    assert (
        isolation.config_dir / "systemd/user/hyprshade.service"
    ).read_text() == "foo"

    write_systemd_user_unit("timer", "bar")
    assert (isolation.config_dir / "systemd/user/hyprshade.timer").read_text() == "bar"


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
