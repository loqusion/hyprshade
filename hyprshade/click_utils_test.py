# mypy: disable-error-code="arg-type"

import click
import pytest

from . import click_utils


class TestClickValidateOptionalParam:
    def test_empty(self):
        assert click_utils.validate_optional_param(None, None, ()) is None

    def test_single(self):
        assert click_utils.validate_optional_param(None, None, ("foo",)) == "foo"

    def test_multiple(self):
        with pytest.raises(click.UsageError):
            click_utils.validate_optional_param(None, None, ("foo", "bar"))
