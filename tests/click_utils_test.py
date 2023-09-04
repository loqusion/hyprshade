# mypy: disable-error-code="arg-type"

import click
import pytest

from hyprshade import click_utils


class TestConvertToShader:
    def test_works(self):
        shader = click_utils.convert_to_shader(None, None, "foo")
        assert shader.name == "foo"

    def test_none(self):
        assert click_utils.convert_to_shader(None, None, None) is None


class TestValidateOptionalParam:
    def test_empty(self):
        assert click_utils.validate_optional_param(None, None, ()) is None

    def test_single(self):
        assert click_utils.validate_optional_param(None, None, ("foo",)) == "foo"

    def test_multiple(self):
        with pytest.raises(click.UsageError):
            click_utils.validate_optional_param(None, None, ("foo", "bar"))


class TestOptionalParam:
    def test_basic(self):
        o = click_utils.optional_param("FOO", None)
        assert o["metavar"] == "FOO"
        assert o["nargs"] == -1
        assert o["callback"] is not None

    def test_callback(self):
        o = click_utils.optional_param("FOO", None)
        callback = o["callback"]
        assert callback(None, None, ("foo",)) == "foo"
        assert callback(None, None, ()) is None

    def test_given_callback(self):
        o = click_utils.optional_param("FOO", lambda *_: "bar")
        callback = o["callback"]
        assert callback(None, None, ("foo",)) == "bar"

    def test_callback_synergy(self):
        o = click_utils.optional_param("FOO", lambda _1, _2, x: x + "bar")
        callback = o["callback"]
        assert callback(None, None, ("foo",)) == "foobar"
