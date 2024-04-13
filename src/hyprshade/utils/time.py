from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import time


def is_time_between(time_: time, start_time: time, end_time: time) -> bool:
    assert start_time != end_time

    if end_time < start_time:
        return start_time <= time_ or time_ < end_time
    return start_time <= time_ < end_time
