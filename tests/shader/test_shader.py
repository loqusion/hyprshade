from pathlib import Path

import pytest

from hyprshade.shader.core import Shader
from tests.types import ShaderPathFactory


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


class TestConstructor:
    def test_name(self):
        assert Shader("foo")._name == "foo"

    def test_path(self, shader_path: Path):
        shader = Shader(str(shader_path))
        assert shader._name == "shader"
        assert shader._given_path == str(shader_path)
        assert shader.does_given_path_exist is True

    def test_nonexistent_path(self, tmp_path: Path):
        shader_path = tmp_path / "foo.glsl"
        if shader_path.exists():
            pytest.fail(f"test assumption failed: {shader_path} exists")

        shader = Shader(str(shader_path))
        assert shader._name == "foo"
        assert shader._given_path == str(shader_path)
        assert shader.does_given_path_exist is False


class TestEquality:
    def test_same_path(self, shader_path_env: Path):
        assert Shader("shader") == Shader("shader")
        assert Shader(str(shader_path_env)) == Shader(str(shader_path_env))
        assert Shader("shader") == Shader(str(shader_path_env))
        assert Shader(str(shader_path_env)) == Shader("shader")

    def test_different_path(self, shader_path_factory: ShaderPathFactory):
        shader_path1 = shader_path_factory("foo")
        shader_path2 = shader_path_factory("bar")

        assert Shader(str(shader_path1)) == Shader("foo")
        assert Shader(str(shader_path2)) == Shader("bar")

        assert Shader("foo") != Shader("bar")
        assert Shader(str(shader_path1)) != Shader(str(shader_path2))
        assert Shader("foo") != Shader(str(shader_path2))
        assert Shader(str(shader_path1)) != Shader("bar")

    def test_other(self, shader_path_env: Path):
        assert Shader("shader") != None  # noqa: E711
        assert Shader("shader") != "shader"
        assert Shader("doesnotexist") != Shader("doesnotexist")


class TestDisplay:
    def test_str(self):
        assert str(Shader("foo")) == "foo"

    def test_repr(self):
        assert repr(Shader("foo")) == "Shader('foo')"

    def test_name(self):
        assert Shader("foo").name == "foo"

    def test_dirname(self, shader_dir_env: Path, shader_path_env: Path):
        assert Shader(str(shader_path_env)).dirname() == str(shader_dir_env.resolve())


@pytest.mark.requires_hyprland
@pytest.mark.usefixtures("_save_screen_shader")
class TestOnOff:
    def test_on(self, shader_path_env: Path):
        Shader("shader").on()
        assert Shader.current() == Shader("shader")

    def test_on_path(self, shader_path: Path):
        Shader(str(shader_path)).on()
        assert Shader.current() == Shader(str(shader_path))

    def test_on_doesnotexist(self):
        with pytest.raises(FileNotFoundError):
            Shader("doesnotexist").on()

    def test_off(self):
        Shader.off()
        assert Shader.current() is None


class TestResolvePath:
    def test_one_path(self, shader_path_env: Path):
        assert Shader("shader")._resolve_path() == str(shader_path_env)

    def test_env_priority(
        self, monkeypatch: pytest.MonkeyPatch, shader_path: Path, tmp_path: Path
    ):
        system_path = tmp_path / "hypr/system/shaders"
        system_path.mkdir(parents=True)
        (system_path / "shader.glsl").touch()

        Shader.dirs.SYSTEM_DIR = str(tmp_path)  # type: ignore[misc]
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, str(shader_path.parent))

        assert Shader("shader")._resolve_path() == str(shader_path)

    def test_given_path(self, shader_path: Path):
        assert Shader(str(shader_path))._resolve_path() == str(shader_path)

    def test_notfound(self, tmp_path: Path, shader_dir_system: Path):
        with pytest.raises(FileNotFoundError):
            Shader("foo")._resolve_path()

        path_not_exist = tmp_path / "foo.glsl"
        if path_not_exist.exists():
            pytest.fail(f"test assumption failed: {path_not_exist} exists")
        with pytest.raises(FileNotFoundError):
            Shader(str(path_not_exist))._resolve_path()

    def test_ignores_cwd(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        shader_path = tmp_path / "foo"
        shader_path.touch()
        monkeypatch.chdir(tmp_path)
        with pytest.raises(FileNotFoundError):
            Shader("foo")._resolve_path()
