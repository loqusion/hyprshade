from hyprshade.shader.core import Shader
from tests.conftest import Isolation


class TestDirs:
    def test_env(self, isolation: Isolation):
        assert str(isolation.hyprshade_env_dir) == Shader.dirs.env()

    def test_user_hypr(self, isolation: Isolation):
        assert (
            str(isolation.hyprshade_user_hypr_dir / "shaders")
            == Shader.dirs.user_hypr()
        )

    def test_user_hyprshade(self, isolation: Isolation):
        assert (
            str(isolation.hyprshade_user_hyprshade_dir / "shaders")
            == Shader.dirs.user_hyprshade()
        )

    def test_system(self, isolation: Isolation):
        assert str(isolation.hyprshade_system_dir / "shaders") == Shader.dirs.system()

    def test_all(self, isolation: Isolation):
        dirs = [
            isolation.hyprshade_env_dir,
            (isolation.hyprshade_user_hypr_dir / "shaders"),
            (isolation.hyprshade_user_hyprshade_dir / "shaders"),
            (isolation.hyprshade_system_dir / "shaders"),
        ]
        assert list(map(str, dirs)) == Shader.dirs.all()
