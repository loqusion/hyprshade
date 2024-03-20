from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import suppress
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from _typeshed import SupportsRead


def render(
    template: SupportsRead | str,
    data: dict[str, Any] | None = None,
) -> str:
    for impl in MustacheImpl.ALL:
        with suppress(MustacheModuleImportError):
            return impl.render(template, data)

    # TODO: Add instructions to install a mustache parser
    raise ImportError("No mustache library found.")


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
