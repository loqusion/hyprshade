from pathlib import Path

import pytest

from hyprshade.shader.core import Shader


class TestDirs:
    def test_env(self, shader_dir_env: Path, monkeypatch: pytest.MonkeyPatch):
        assert str(shader_dir_env) == Shader.dirs.env()
        monkeypatch.delenv(Shader.dirs.ENV_VAR_NAME, raising=False)
        assert Shader.dirs.env() != str(shader_dir_env)

    def test_user_hypr(self, shader_dir_user: Path):
        assert Shader.dirs.user_hypr() == str(shader_dir_user)

    def test_system(self, shader_dir_system: Path):
        assert str(shader_dir_system) == Shader.dirs.system()

    def test_all(
        self,
        shader_dir_env: Path,
        shader_dir_user: Path,
        shader_dir_system: Path,
    ):
        assert Shader.dirs.all() == list(
            map(str, [shader_dir_env, shader_dir_user, shader_dir_system])
        )
