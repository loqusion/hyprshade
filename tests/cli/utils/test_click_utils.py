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
