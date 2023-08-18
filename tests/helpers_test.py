from pathlib import Path

import pytest

from hyprshade import helpers


def test_write_systemd_user_unit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    (tmp_path / "systemd" / "user").mkdir(parents=True)

    helpers.write_systemd_user_unit("service", "foo")
    assert (tmp_path / "systemd" / "user" / "hyprshade.service").read_text() == "foo"

    helpers.write_systemd_user_unit("timer", "bar")
    assert (tmp_path / "systemd" / "user" / "hyprshade.timer").read_text() == "bar"
