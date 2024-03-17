from __future__ import annotations

from os import path
from typing import Final


def stripped_basename(s: str) -> str:
    return strip_all_extensions(path.basename(s))


MAX_ITERATIONS: Final = 99


def strip_all_extensions(name: str) -> str:
    for _ in range(MAX_ITERATIONS):
        name, ext = path.splitext(name)
        if not ext:
            return name

    raise ValueError(f"Max iterations reached while stripping extensions from '{name}")
