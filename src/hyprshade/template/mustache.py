from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _typeshed import SupportsRead


def render(
    template: SupportsRead | str,
    data: dict[str, Any] | None = None,
):
    try:
        return ChevronImpl.render(template, data)
    except ImportError:
        pass

    try:
        return PystacheImpl.render(template, data)
    except ImportError:
        pass

    raise ImportError("No mustache library found.")


class ChevronImpl:
    @classmethod
    def render(
        cls,
        template: SupportsRead[str] | str,
        data: dict[str, Any] | None = None,
        *args,
        **kwargs,
    ) -> str:
        import chevron

        if data is None:
            data = {}

        return chevron.render(template, data, *args, **kwargs)


class PystacheImpl:
    @classmethod
    def render(cls, template: SupportsRead[str] | str, context=None) -> str:
        import pystache  # type: ignore[import-not-found, import-untyped]

        template = cls._coerce_template_to_str(template)
        return pystache.render(template, context or {})

    @staticmethod
    def _coerce_template_to_str(template: SupportsRead[str] | str) -> str:
        if isinstance(template, str):
            return template
        return template.read()
