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

    assert_no_duplicate_keys(data or {}, DEFAULT_RENDER_DATA)

    return chevron.render(template, {**DEFAULT_RENDER_DATA, **(data or {})})


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
        case [_, _, *_]:
            raise ValueError(
                "Mustache nullish coalesce operator must occur only once in an expression."
            )
        case _:
            raise ValueError("Mustache nullish coalesce operator is not valid.")


NULLISH_COALESCE_LAMBDA_NAME: Final = "d"
DEFAULT_RENDER_DATA: Final = {NULLISH_COALESCE_LAMBDA_NAME: nullish_coalesce}


def assert_no_duplicate_keys(d1: dict, d2: dict) -> None:
    duplicate_keys = d1.keys() & d2.keys()
    if duplicate_keys:
        # TODO: Improve error message
        raise ValueError(f"Invalid data keys: {', '.join(duplicate_keys)}")
