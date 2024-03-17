from pathlib import Path

import pytest

from hyprshade.utils.xdg import user_config_dir


class TestUserConfigDir:
    def test_uses_xdg_config_home(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("XDG_CONFIG_HOME", tmp_path.as_posix())
        assert user_config_dir("hyprshade") == (tmp_path / "hyprshade").as_posix()

    def test_uses_home(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.setenv("HOME", str(tmp_path))
        assert (
            user_config_dir("hyprshade") == (tmp_path / ".config/hyprshade").as_posix()
        )
