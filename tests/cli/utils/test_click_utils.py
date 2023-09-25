# mypy: disable-error-code="arg-type"

from pathlib import Path

import click
import pytest

from hyprshade.cli import utils


class TestConvertToShader:
    def test_works(self):
        shader = utils.convert_to_shader(None, None, "foo")
        assert shader is not None
        assert shader.name == "foo"

    def test_none(self):
        assert utils.convert_to_shader(None, None, None) is None

    def test_stale(self):
        if Path("./foo").exists():
            pytest.fail("test assumption failed: ./foo exists")

        with pytest.raises(click.BadParameter):
            utils.convert_to_shader(None, None, "./foo")


class TestValidateOptionalParam:
    def test_empty(self):
        assert utils.validate_optional_param(None, None, ()) is None

    def test_single(self):
        assert utils.validate_optional_param(None, None, ("foo",)) == "foo"

    def test_rejects_multiple(self):
        with pytest.raises(click.UsageError):
            utils.validate_optional_param(None, None, ("foo", "bar"))


class TestOptionalParam:
    def test_basic(self):
        o = utils.optional_param("FOO", None)
        assert o["metavar"] == "FOO"
        assert o["nargs"] == -1
        assert o["callback"] is not None

    def test_callback(self):
        o = utils.optional_param("FOO", None)
        callback = o["callback"]
        assert callback(None, None, ("foo",)) == "foo"
        assert callback(None, None, ()) is None

    def test_given_callback(self):
        o = utils.optional_param("FOO", lambda *_: "bar")
        callback = o["callback"]
        assert callback(None, None, ("foo",)) == "bar"

    def test_callback_synergy(self):
        o = utils.optional_param("FOO", lambda _1, _2, x: x + "bar")
        callback = o["callback"]
        assert callback(None, None, ("foo",)) == "foobar"
