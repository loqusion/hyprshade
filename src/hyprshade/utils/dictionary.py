from __future__ import annotations

from typing import Literal, TypeAlias

DeepMergeStrategy: TypeAlias = Literal["force", "keep"]


def __deep_merge_impl(
    dest: dict, source: dict, /, *, strategy: DeepMergeStrategy
) -> dict:
    for key in source:
        if key in dest:
            if isinstance(dest[key], dict) and isinstance(source[key], dict):
                __deep_merge_impl(dest[key], source[key], strategy=strategy)
            elif strategy == "force":
                dest[key] = source[key]
        else:
            dest[key] = source[key]

    return dest


def deep_merge(
    destination: dict, /, *dicts: dict, strategy: DeepMergeStrategy = "force"
) -> dict:
    """Merge multiple dictionaries recursively.

    `destination` will be mutated in place and returned. Items will only
    be merged if they are both instances of `dict`; if not, the behavior will be
    determined by `strategy`.

    If `strategy` is `"force"`, values from the rightmost dictionary will be used.
    If `strategy` is `"keep"`, values from the leftmost dictionary will be used.
    """

    for d in dicts:
        __deep_merge_impl(destination, d, strategy=strategy)

    return destination
