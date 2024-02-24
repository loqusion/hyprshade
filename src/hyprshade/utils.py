from __future__ import annotations

import os
from os import path
from typing import TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import time

    from _typeshed import GenericPath


def is_time_between(time_: time, start_time: time, end_time: time) -> bool:
    if end_time <= start_time:
        return start_time <= time_ or time_ <= end_time
    return start_time <= time_ <= end_time


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


def stripped_basename(s: str) -> str:
    return path.splitext(path.basename(s))[0]
