from pathlib import Path

import pytest

from hyprshade.shader import Shader, _stripped_basename


class TestDirs:
    def test_env(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, "/foo/bar")
        assert Shader.dirs.env() == "/foo/bar"
        monkeypatch.delenv(Shader.dirs.ENV_VAR_NAME, raising=False)
        assert Shader.dirs.env() == "$" + Shader.dirs.ENV_VAR_NAME

    def test_system(self):
        assert Shader.dirs.system() == Shader.dirs.SYSTEM_DIR

    def test_user(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        assert Shader.dirs.user() == str(tmp_path / "hypr/shaders")

    def test_all(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        env_path = tmp_path / "hypr/env/shaders"
        env_path.mkdir(parents=True)
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, str(env_path))

        system_path = tmp_path / "hypr/system/shaders"
        system_path.mkdir(parents=True)
        Shader.dirs.SYSTEM_DIR = str(system_path)  # type: ignore[misc]

        user_path = tmp_path / "hypr/shaders"
        user_path.mkdir(parents=True)
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

        assert Shader.dirs.all() == list(map(str, [env_path, system_path, user_path]))


class TestConstructor:
    def test_name(self):
        assert Shader("foo")._name == "foo"

    def test_path(self, shader_path: Path):
        shader = Shader(str(shader_path))
        assert shader._name == "shader"
        assert shader._given_path == str(shader_path)

    def test_nonexistent_path(self, tmp_path: Path):
        shader_path = tmp_path / "foo.glsl"
        assert not shader_path.exists(), "test assumption failed"

        shader = Shader(str(shader_path))
        assert shader._name == "foo"
        assert shader._given_path is None


class TestEquality:
    def test_same_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, str(tmp_path))
        shader_path = tmp_path / "foo.glsl"
        shader_path.touch()

        assert Shader("foo") == Shader("foo")
        assert Shader(str(shader_path)) == Shader(str(shader_path))
        assert Shader("foo") == Shader(str(shader_path))
        assert Shader(str(shader_path)) == Shader("foo")

    def test_different_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, str(tmp_path))
        shader_path1 = tmp_path / "foo.glsl"
        shader_path2 = tmp_path / "bar.glsl"
        shader_path1.touch()
        shader_path2.touch()

        assert Shader("foo") != Shader("bar")
        assert Shader(str(shader_path1)) != Shader(str(shader_path2))
        assert Shader("foo") != Shader(str(shader_path2))
        assert Shader(str(shader_path1)) != Shader("bar")

    def test_other(self):
        assert Shader("foo") != None  # noqa: E711
        assert Shader("foo") != "foo"


class TestDisplay:
    def test_str(self):
        assert str(Shader("foo")) == "foo"

    def test_repr(self):
        assert repr(Shader("foo")) == "Shader('foo')"

    def test_name(self):
        assert Shader("foo").name == "foo"


@pytest.mark.hyprland()
@pytest.mark.usefixtures("_save_screen_shader")
class TestOnOff:
    def test_on(self, monkeypatch: pytest.MonkeyPatch, shader_path: Path):
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, str(shader_path.parent))
        name = _stripped_basename(str(shader_path))
        Shader(name).on()
        assert Shader.current() == Shader(name)

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
    def test_one_path(self, monkeypatch: pytest.MonkeyPatch, shader_path: Path):
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, str(shader_path.parent))
        assert Shader("shader")._resolve_path() == str(shader_path)

    def test_env_priority(
        self, monkeypatch: pytest.MonkeyPatch, shader_path: Path, tmp_path: Path
    ):
        system_path = tmp_path / "hypr/system/shaders"
        system_path.mkdir(parents=True)
        (system_path / "shader.glsl").touch()
        assert (system_path / "shader.glsl").exists(), "test assumption failed"

        Shader.dirs.SYSTEM_DIR = str(tmp_path)  # type: ignore[misc]
        monkeypatch.setenv(Shader.dirs.ENV_VAR_NAME, str(shader_path.parent))

        assert Shader("shader")._resolve_path() == str(shader_path)

    def test_given_path(self, shader_path: Path):
        assert Shader(str(shader_path))._resolve_path() == str(shader_path)

    def test_notfound(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            Shader("foo")._resolve_path()

        path_not_exist = tmp_path / "foo.glsl"
        assert not path_not_exist.exists(), "test assumption failed"
        with pytest.raises(FileNotFoundError):
            Shader(str(path_not_exist))._resolve_path()

    def test_ignores_cwd(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        shader_path = tmp_path / "foo.glsl"
        shader_path.touch()
        monkeypatch.chdir(tmp_path)
        with pytest.raises(FileNotFoundError):
            Shader("foo")._resolve_path()
