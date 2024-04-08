from pathlib import Path

import pytest

from hyprshade.shader import hyprctl
from hyprshade.shader.core import PureShader, Shader
from tests.types import HyprshadeDirectoryName, ShaderPathFactory


class ShaderNoConfig(Shader):
    def __init__(self, shader_name_or_path: str):
        super().__init__(shader_name_or_path, None)


class TestPureShaderConstructor:
    def test_name(self):
        shader = PureShader("foo")
        assert shader._name == "foo"
        assert shader._given_path is None

    def test_invalid_name(self):
        with pytest.raises(ValueError, match="must not contain a '.' character"):
            _shader = PureShader("foo.glsl")

    def test_path(self, tmp_path: Path):
        shader_path = tmp_path / "foo.glsl"
        shader = PureShader(str(shader_path))

        assert shader._name == "foo"
        assert shader._given_path == str(shader_path)


class TestPureShaderEq:
    def test_basic(self):
        assert PureShader("foo") != None  # noqa: E711
        assert PureShader("foo") != "foo"
        assert PureShader("foo") != PureShader("bar")
        assert PureShader("foo") != PureShader("foo")

    def test_with_paths(self, shader_path_factory: ShaderPathFactory):
        shader_path1 = shader_path_factory("foo")
        shader_path2 = shader_path_factory("bar")

        assert PureShader("foo") == PureShader("foo")
        assert PureShader(str(shader_path1)) == PureShader(str(shader_path1))
        assert PureShader(str(shader_path1)) == PureShader("foo")

        assert PureShader("foo") != PureShader("bar")
        assert PureShader(str(shader_path1)) != PureShader(str(shader_path2))
        assert PureShader("foo") != PureShader(str(shader_path2))
        assert PureShader(str(shader_path1)) != PureShader("bar")


class TestPureShaderDisplay:
    def test_str(self):
        assert str(PureShader("foo")) == "foo"

    def test_repr(self):
        class ShaderSubclass(PureShader):
            pass

        assert repr(PureShader("foo")) == "PureShader('foo')"
        assert repr(ShaderSubclass("foo")) == "ShaderSubclass('foo')"


class TestPureShaderName:
    def test_str(self):
        assert PureShader("foo").name == "foo"

    def test_path(self, tmp_path_factory: pytest.TempPathFactory):
        shader_path = tmp_path_factory.mktemp("foo.glsl")
        assert PureShader(str(shader_path)).name == "foo"

    def test_path_multiple_extensions(self, tmp_path_factory: pytest.TempPathFactory):
        shader_path = tmp_path_factory.mktemp("foo.glsl.mustache")
        assert PureShader(str(shader_path)).name == "foo"


class TestPureShaderResolvePath:
    def test_given_path(self, shader_path: Path):
        assert PureShader(str(shader_path))._resolve_path() == str(shader_path)

    def test_given_path_not_exist(self, tmp_path: Path):
        path_not_exist = tmp_path / "foo.glsl"
        if path_not_exist.exists():
            pytest.fail(f"test assumption failed: {path_not_exist} exists")
        with pytest.raises(FileNotFoundError):
            PureShader(str(path_not_exist))._resolve_path()

    @pytest.mark.parametrize(
        "directory_name", ["env", "user_hypr", "user_hyprshade", "system"]
    )
    def test_resolves_from(
        self,
        directory_name: HyprshadeDirectoryName,
        shader_path_factory: ShaderPathFactory,
    ):
        shader_path = shader_path_factory("shader", directory_name)
        assert PureShader("shader")._resolve_path() == str(shader_path)

    @pytest.mark.parametrize(
        ("priority_directory_name", "other_directory_name"),
        [
            ("env", "user_hypr"),
            ("env", "user_hyprshade"),
            ("env", "system"),
            ("user_hypr", "system"),
            ("user_hyprshade", "system"),
        ],
    )
    def test_priority(
        self,
        priority_directory_name: HyprshadeDirectoryName,
        other_directory_name: HyprshadeDirectoryName,
        shader_path_factory: ShaderPathFactory,
    ):
        priority_shader_path = shader_path_factory("shader", priority_directory_name)
        _other_shader_path = shader_path_factory("shader", other_directory_name)

        assert PureShader("shader")._resolve_path() == str(priority_shader_path)

    def test_ignores_cwd(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "foo.glsl").touch()
        with pytest.raises(FileNotFoundError):
            PureShader("foo")._resolve_path()


@pytest.mark.requires_hyprland()
class TestShaderOnOff:
    @pytest.mark.parametrize(
        "directory_name", ["env", "user_hypr", "user_hyprshade", "system"]
    )
    def test_on_and_off(
        self,
        directory_name: HyprshadeDirectoryName,
        shader_path_factory: ShaderPathFactory,
    ):
        shader_path = shader_path_factory("shader", directory_name)
        ShaderNoConfig("shader").on()
        assert hyprctl.get_screen_shader() == str(shader_path)

        ShaderNoConfig.off()
        assert hyprctl.get_screen_shader() is None

    def test_on_given_path(self, shader_path: Path):
        ShaderNoConfig(str(shader_path)).on()
        assert hyprctl.get_screen_shader() == str(shader_path)

    def test_on_not_exist(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            ShaderNoConfig("doesnotexist").on()
        with pytest.raises(FileNotFoundError):
            ShaderNoConfig(str(tmp_path / "doesnotexist.glsl")).on()


class TestShaderTemplate:
    pass


class TestShaderIntegration:
    @pytest.mark.requires_hyprland()
    @pytest.mark.parametrize("is_template", [False, True])
    def test_on_off_current_eq(
        self, is_template: bool, shader_path_factory: ShaderPathFactory
    ):
        if is_template:
            # FIXME: Confused shader identity results in buggy `hyprshade toggle`
            pytest.skip(
                "Template shader identity is buggy since the rendered path is different from the source path"
            )

        shader_path = shader_path_factory(
            "shader", extension=("glsl" if not is_template else "glsl.mustache")
        )
        shader = ShaderNoConfig(str(shader_path))

        Shader.off()
        assert Shader.current() is None

        shader.on()
        assert Shader.current() == shader
