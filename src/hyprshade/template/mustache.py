from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _typeshed import SupportsRead


def render(
    template: SupportsRead | str,
    data: dict[str, Any] | None = None,
):
    if data is None:
        data = {}

    try:
        return chevron_render(template, data)
    except ImportError:
        pass

    try:
        return pystache_render(template, data)
    except ImportError:
        pass

    raise ImportError("No mustache library found.")


def chevron_render(*args, **kwargs) -> str:
    import chevron

    return chevron.render(*args, **kwargs)


def pystache_render(template: SupportsRead[str] | str, context=None) -> str:
    import pystache  # type: ignore[import-not-found, import-untyped]

    template = coerce_template_to_str(template)
    return pystache.render(template, context or {})


def coerce_template_to_str(template: SupportsRead[str] | str) -> str:
    if isinstance(template, str):
        return template
    return template.read()
