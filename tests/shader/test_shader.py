from pathlib import Path

import pytest

from hyprshade.shader.core import Shader
from tests.types import ShaderPathFactory


class ShaderNoConfig(Shader):
    def __init__(self, shader_name_or_path: str):
        super().__init__(shader_name_or_path, None)


class TestConstructor:
    def test_name(self):
        assert ShaderNoConfig("foo")._name == "foo"

    def test_path(self, shader_path: Path):
        shader = ShaderNoConfig(str(shader_path))
        assert shader._name == "shader"
        assert shader._given_path == str(shader_path)
        assert shader.does_given_path_exist is True

    def test_nonexistent_path(self, tmp_path: Path):
        shader_path = tmp_path / "foo.glsl"
        if shader_path.exists():
            pytest.fail(f"test assumption failed: {shader_path} exists")

        shader = ShaderNoConfig(str(shader_path))
        assert shader._name == "foo"
        assert shader._given_path == str(shader_path)
        assert shader.does_given_path_exist is False


class TestEquality:
    def test_same_path(self, shader_path_env: Path):
        assert ShaderNoConfig("shader") == ShaderNoConfig("shader")
        assert ShaderNoConfig(str(shader_path_env)) == ShaderNoConfig(
            str(shader_path_env)
        )
        assert ShaderNoConfig("shader") == ShaderNoConfig(str(shader_path_env))
        assert ShaderNoConfig(str(shader_path_env)) == ShaderNoConfig("shader")

    def test_different_path(self, shader_path_factory: ShaderPathFactory):
        shader_path1 = shader_path_factory("foo")
        shader_path2 = shader_path_factory("bar")

        assert ShaderNoConfig(str(shader_path1)) == ShaderNoConfig("foo")
        assert ShaderNoConfig(str(shader_path2)) == ShaderNoConfig("bar")

        assert ShaderNoConfig("foo") != ShaderNoConfig("bar")
        assert ShaderNoConfig(str(shader_path1)) != ShaderNoConfig(str(shader_path2))
        assert ShaderNoConfig("foo") != ShaderNoConfig(str(shader_path2))
        assert ShaderNoConfig(str(shader_path1)) != ShaderNoConfig("bar")

    def test_other(self, shader_path_env: Path):
        assert ShaderNoConfig("shader") != None  # noqa: E711
        assert ShaderNoConfig("shader") != "shader"
        assert ShaderNoConfig("doesnotexist") != ShaderNoConfig("doesnotexist")


class TestDisplay:
    def test_str(self):
        assert str(ShaderNoConfig("foo")) == "foo"

    @pytest.mark.skip("TODO: fix this test")
    def test_repr(self):
        assert repr(ShaderNoConfig("foo")) == "Shader('foo')"

    def test_name(self):
        assert ShaderNoConfig("foo").name == "foo"

    def test_dirname(self, shader_dir_env: Path, shader_path_env: Path):
        assert ShaderNoConfig(str(shader_path_env)).dirname() == str(
            shader_dir_env.resolve()
        )


@pytest.mark.requires_hyprland()
class TestOnOff:
    def test_on(self, shader_path_env: Path):
        ShaderNoConfig("shader").on()
        assert ShaderNoConfig.current() == ShaderNoConfig("shader")

    def test_on_path(self, shader_path: Path):
        ShaderNoConfig(str(shader_path)).on()
        assert ShaderNoConfig.current() == ShaderNoConfig(str(shader_path))

    def test_on_doesnotexist(self):
        with pytest.raises(FileNotFoundError):
            ShaderNoConfig("doesnotexist").on()

    def test_off(self):
        ShaderNoConfig.off()
        assert ShaderNoConfig.current() is None


class TestResolvePath:
    def test_one_path(self, shader_path_env: Path):
        assert ShaderNoConfig("shader")._resolve_path() == str(shader_path_env)

    def test_env_priority(
        self, monkeypatch: pytest.MonkeyPatch, shader_path: Path, tmp_path: Path
    ):
        system_path = tmp_path / "hypr/system/shaders"
        system_path.mkdir(parents=True)
        (system_path / "shader.glsl").touch()

        ShaderNoConfig.dirs.SYSTEM_DIR = str(tmp_path)  # type: ignore[misc]
        monkeypatch.setenv(ShaderNoConfig.dirs.ENV_VAR_NAME, str(shader_path.parent))

        assert ShaderNoConfig("shader")._resolve_path() == str(shader_path)

    def test_given_path(self, shader_path: Path):
        assert ShaderNoConfig(str(shader_path))._resolve_path() == str(shader_path)

    def test_notfound(self, tmp_path: Path, shader_dir_system: Path):
        with pytest.raises(FileNotFoundError):
            ShaderNoConfig("foo")._resolve_path()

        path_not_exist = tmp_path / "foo.glsl"
        if path_not_exist.exists():
            pytest.fail(f"test assumption failed: {path_not_exist} exists")
        with pytest.raises(FileNotFoundError):
            ShaderNoConfig(str(path_not_exist))._resolve_path()

    def test_ignores_cwd(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        shader_path = tmp_path / "foo"
        shader_path.touch()
        monkeypatch.chdir(tmp_path)
        with pytest.raises(FileNotFoundError):
            ShaderNoConfig("foo")._resolve_path()
