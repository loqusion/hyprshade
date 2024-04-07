from __future__ import annotations

import re
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from collections.abc import Callable

    from _typeshed import SupportsRead


def render(
    template: SupportsRead[str] | str,
    data: dict[str, Any] | None = None,
) -> str:
    assert_no_duplicate_keys(data or {}, DEFAULT_RENDER_DATA)
    data = {**DEFAULT_RENDER_DATA, **(data or {})}
    for impl in MustacheImpl.ALL:
        with suppress(MustacheModuleImportError):
            return impl.render(template, data)

    # TODO: Add instructions to install a mustache parser
    raise ImportError("No mustache library found.")


NULLISH_COALESCE_OPERATOR_PATTERN: Final = re.compile(r"\s*\?\s*")


def nullish_coalesce(text: str, render: Callable[[str], str]):
    lhs, *rhs = NULLISH_COALESCE_OPERATOR_PATTERN.split(text)
    match len(rhs):
        case 0:
            raise ValueError(
                "Mustache nullish coalesce operator requires a default value."
            )
        case 1:
            rendered_lhs = render(lhs)
            return rendered_lhs if rendered_lhs.strip() else render(rhs[0])
        case _:
            raise ValueError(
                "Mustache nullish coalesce operator must occur only once in an expression."
            )


NULLISH_COALESCE_LAMBDA_NAME: Final = "d"
DEFAULT_RENDER_DATA: Final = {NULLISH_COALESCE_LAMBDA_NAME: nullish_coalesce}


def assert_no_duplicate_keys(d1: dict, d2: dict) -> None:
    duplicate_keys = d1.keys() & d2.keys()
    if duplicate_keys:
        # TODO: Improve error message
        raise ValueError(f"Invalid data keys: {', '.join(duplicate_keys)}")


class MustacheModuleImportError(ImportError):
    pass


class MustacheImpl(ABC):
    ALL: Final[list[type[MustacheImpl]]]  # type:ignore[misc]

    @classmethod
    @abstractmethod
    def render(
        cls,
        template: SupportsRead[str] | str,
        data: dict[str, Any] | None = None,
        *args,
        **kwargs,
    ) -> str:
        try:
            module = cls._import_module()
        except ImportError as e:
            raise MustacheModuleImportError(e) from e

        return module.render(template, data, *args, **kwargs)

    @staticmethod
    @abstractmethod
    def _import_module() -> Any: ...


class ChevronImpl(MustacheImpl):
    @classmethod
    def render(
        cls,
        template: SupportsRead[str] | str,
        data: dict[str, Any] | None = None,
        *args,
        **kwargs,
    ) -> str:
        return super().render(template, data or {}, *args, **kwargs)

    @staticmethod
    def _import_module():
        import chevron

        return chevron


class PystacheImpl(MustacheImpl):
    @classmethod
    def render(cls, template: SupportsRead[str] | str, context=None) -> str:
        template = cls._coerce_template_to_str(template)
        return super().render(template, context or {})

    @staticmethod
    def _import_module():
        import pystache  # type: ignore[import-not-found, import-untyped]

        return pystache

    @staticmethod
    def _coerce_template_to_str(template: SupportsRead[str] | str) -> str:
        if isinstance(template, str):
            return template
        return template.read()


MustacheImpl.ALL = [ChevronImpl, PystacheImpl]  # type:ignore[misc]
