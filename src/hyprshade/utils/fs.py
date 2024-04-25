from __future__ import annotations

import os
from os import PathLike
from typing import TYPE_CHECKING, AnyStr

from more_itertools import flatten

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

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


def ls_dirs(dirs: Iterable[str | PathLike[str]]) -> Iterator[str]:
    all_files = flatten(scandir_recursive(d, max_depth=5) for d in dirs)
    return (f.path for f in sorted(all_files, key=lambda f: f.name))
