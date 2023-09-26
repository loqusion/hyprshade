from pathlib import Path

import pytest

from hyprshade.cli.utils import ls_dirs, write_systemd_user_unit


class TestLsDirs:
    def test_empty(self):
        assert list(ls_dirs([])) == []

    def test_single(self, tmp_path: Path):
        (tmp_path / "foo").touch()
        assert list(ls_dirs([tmp_path])) == ["foo"]

    def test_multiple(self, tmp_path: Path):
        (tmp_path / "foo").touch()
        (tmp_path / "bar").touch()
        assert list(ls_dirs([tmp_path])) == ["bar", "foo"]

    def test_multiple_dirs(self, tmp_path_factory: pytest.TempPathFactory):
        paths = []
        for dir_ in ["foo", "bar", "baz"]:
            tmp_path_ = tmp_path_factory.mktemp(dir_)
            (tmp_path_ / f"qux{dir_}").touch()
            paths.append(tmp_path_)

        assert list(ls_dirs(paths)) == ["quxbar", "quxbaz", "quxfoo"]

    def test_unique(self, tmp_path_factory: pytest.TempPathFactory):
        paths = []
        for dir_ in ["foo", "bar", "baz"]:
            tmp_path_ = tmp_path_factory.mktemp(dir_)
            (tmp_path_ / "qux").touch()
            paths.append(tmp_path_)

        assert list(ls_dirs(paths)) == ["qux"]


def test_write_systemd_user_unit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    (tmp_path / "systemd" / "user").mkdir(parents=True)

    write_systemd_user_unit("service", "foo")
    assert (tmp_path / "systemd" / "user" / "hyprshade.service").read_text() == "foo"

    write_systemd_user_unit("timer", "bar")
    assert (tmp_path / "systemd" / "user" / "hyprshade.timer").read_text() == "bar"
