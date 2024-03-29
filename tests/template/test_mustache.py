import pytest

from hyprshade.template.mustache import render


class TestChevron:
    def test_chevron_enabled(self):
        from importlib.util import find_spec

        assert find_spec("chevron") is not None

    def test_basic(self):
        assert render("Hello, world!") == "Hello, world!"

    def test_variable(self):
        assert render("Hello, {{name}}!", {"name": "world"}) == "Hello, world!"

    def test_default_variable(self):
        template = "Hello, {{#name}}{{.}}{{/name}}{{^name}}world{{/name}}!"

        assert render(template, {"name": "planet"}) == "Hello, planet!"
        assert render(template) == "Hello, world!"


@pytest.mark.requires_pystache()
@pytest.mark.usefixtures("_disable_chevron")
class TestPystache:
    def test_chevron_disabled(self):
        from importlib.util import find_spec

        assert find_spec("chevron") is None

    def test_basic(self):
        assert render("Hello, world!") == "Hello, world!"

    def test_variable(self):
        assert render("Hello, {{name}}!", {"name": "world"}) == "Hello, world!"

    def test_default_variable(self):
        template = "Hello, {{#name}}{{.}}{{/name}}{{^name}}world{{/name}}!"

        assert render(template, {"name": "planet"}) == "Hello, planet!"
        assert render(template) == "Hello, world!"


@pytest.fixture(scope="class")
def _disable_chevron():
    import sys

    sys.modules["chevron"] = None  # type: ignore[assignment]

    yield

    sys.modules.pop("chevron")
