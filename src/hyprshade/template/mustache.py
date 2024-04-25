from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from collections.abc import Callable

    from _typeshed import SupportsRead


def render(
    template: SupportsRead[str] | str,
    data: dict[str, Any] | None = None,
) -> str:
    import chevron

    if data is not None:
        raise_if_reserved_keys(data)

    return chevron.render(template, DEFAULT_RENDER_DATA | (data or {}))


NULLISH_COALESCE_OPERATOR_PATTERN: Final = re.compile(r"\s*\?\s*")


def nullish_coalesce(text: str, render: Callable[[str], str]):
    match NULLISH_COALESCE_OPERATOR_PATTERN.split(text):
        case [_]:
            raise ValueError(
                "Mustache nullish coalesce operator requires a default value."
            )
        case [lhs, rhs]:
            rendered_lhs = render(lhs)
            return rendered_lhs if rendered_lhs.strip() else render(rhs)
        case [_, _, _, *_]:
            raise ValueError(
                "Mustache nullish coalesce operator must occur only once in an expression."
            )
        case _:
            raise ValueError("Mustache nullish coalesce operator is not valid.")


NULLISH_COALESCE_LAMBDA_NAME: Final = "nc"
DEFAULT_RENDER_DATA: Final = {NULLISH_COALESCE_LAMBDA_NAME: nullish_coalesce}


def raise_if_reserved_keys(d: dict) -> None:
    if duplicate_keys := d.keys() & DEFAULT_RENDER_DATA.keys():
        raise ReservedVariablesError(duplicate_keys)


class ReservedVariablesError(Exception):
    def __init__(self, duplicate_keys: set[str]) -> None:
        self.duplicate_keys = duplicate_keys
        super().__init__(
            f"Invalid variable name{'s' if len(duplicate_keys) != 1 else ''}: {', '.join(duplicate_keys)}"
        )
        self.add_note(
            f"The following names are reserved: {', '.join(DEFAULT_RENDER_DATA.keys())}"
        )

    def __repr__(self) -> str:
        return f"ReservedVariablesError({self.duplicate_keys!r})"
