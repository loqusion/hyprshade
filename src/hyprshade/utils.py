from __future__ import annotations

import os
from typing import TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import time

    from _typeshed import GenericPath


def is_time_between(time_: time, start_time: time, end_time: time) -> bool:
    if end_time <= start_time:
        return start_time <= time_ or time_ <= end_time
    return start_time <= time_ <= end_time


def scandir_recursive(path: GenericPath[AnyStr]) -> Iterator[os.DirEntry[AnyStr]]:
    dir_queue = []

    with os.scandir(path) as it:
        for direntry in it:
            if direntry.is_dir():
                dir_queue.append(direntry)
            else:
                yield direntry

    while dir_queue:
        yield from scandir_recursive(dir_queue.pop())
