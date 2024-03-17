from __future__ import annotations

import os
from typing import TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    from collections.abc import Iterator

    from _typeshed import GenericPath


def scandir_recursive(
    path: GenericPath[AnyStr], *, max_depth: int
) -> Iterator[os.DirEntry[AnyStr]]:
    assert max_depth >= 0

    dir_stack = []

    with os.scandir(path) as it:
        for direntry in it:
            if not direntry.is_dir():
                yield direntry
            elif max_depth > 0:
                dir_stack.append(direntry)

    while dir_stack:
        yield from scandir_recursive(dir_stack.pop(), max_depth=max_depth - 1)
