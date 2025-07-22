from collections.abc import Callable

import pytest
from click.shell_completion import CompletionItem

from hyprshade.cli.utils import ShaderParamType
from tests.types import ShaderPathFactory

pytestmark = [pytest.mark.usefixtures("_clear_shader_env")]


@pytest.fixture
def _shaders(shader_path_factory: ShaderPathFactory):
    shader_path_factory("foo")
    shader_path_factory("bar")


ShaderComplete = Callable[[str], list[CompletionItem]]


@pytest.fixture
def shader_complete() -> ShaderComplete:
    shader_param = ShaderParamType()

    def _shader_complete(incomplete: str):
        return shader_param.shell_complete(None, None, incomplete)  # type: ignore[arg-type]

    return _shader_complete


def test_shell_complete_empty(shader_complete: ShaderComplete):
    assert shader_complete("foo") == []


@pytest.mark.usefixtures("_shaders")
def test_shell_complete(shader_complete: ShaderComplete):
    completion_items = shader_complete("foo")

    for expected_value, item in zip(["bar", "foo"], completion_items, strict=True):
        assert item.value == expected_value


def test_shell_complete_path(shader_complete: ShaderComplete):
    completion_items = shader_complete("./")

    for expected_value, item in zip(["./"], completion_items, strict=True):
        assert item.value == expected_value
