from pathlib import Path

import pytest

from hyprshade.cli.ls import ls_dirs
from hyprshade.cli.utils import ContextObject, write_systemd_user_unit
from tests.conftest import Isolation
from tests.types import ConfigFactory


class TestLsDirs:
    def test_empty(self):
        assert list(ls_dirs([])) == []

    def test_single(self, tmp_path: Path):
        (tmp_file := tmp_path / "foo").touch()
        assert list(ls_dirs([tmp_path])) == [str(tmp_file)]

    def test_multiple(self, tmp_path: Path):
        (tmp_file1 := tmp_path / "bar").touch()
        (tmp_file2 := tmp_path / "foo").touch()
        assert list(ls_dirs([tmp_path])) == list(map(str, [tmp_file1, tmp_file2]))

    def test_multiple_dirs(self, tmp_path_factory: pytest.TempPathFactory):
        paths = []
        for name in ["foo", "bar", "baz"]:
            tmp_path = tmp_path_factory.mktemp(name)
            (tmp_path / f"qux{name}").touch()
            paths.append(tmp_path)

        assert list(ls_dirs(paths)) == list(
            map(
                str,
                [
                    paths[1] / "quxbar",
                    paths[2] / "quxbaz",
                    paths[0] / "quxfoo",
                ],
            )
        )


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
