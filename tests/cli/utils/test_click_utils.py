# mypy: disable-error-code="arg-type"

import click
import pytest

from hyprshade.cli import utils


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
        o = utils.optional_param("FOO")
        assert o["metavar"] == "FOO"
        assert o["nargs"] == -1
        assert o["callback"] is not None

    def test_callback(self):
        o = utils.optional_param("FOO")
        callback = o["callback"]
        assert callback(None, None, ("foo",)) == "foo"
        assert callback(None, None, ()) is None

    def test_given_callback(self):
        o = utils.optional_param("FOO", callback=lambda *_: "bar")
        callback = o["callback"]
        assert callback(None, None, ("foo",)) == "bar"

    def test_callback_synergy(self):
        o = utils.optional_param("FOO", callback=lambda _1, _2, x: x + "bar")
        callback = o["callback"]
        assert callback(None, None, ("foo",)) == "foobar"
