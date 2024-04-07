from hyprshade.template.mustache import render


def test_chevron_enabled():
    from importlib.util import find_spec

    assert find_spec("chevron") is not None


def test_basic():
    assert render("Hello, world!") == "Hello, world!"


def test_variable():
    assert render("Hello, {{name}}!", {"name": "world"}) == "Hello, world!"


def test_default_variable():
    template = "Hello, {{#name}}{{.}}{{/name}}{{^name}}world{{/name}}!"

    assert render(template, {"name": "planet"}) == "Hello, planet!"
    assert render(template) == "Hello, world!"
