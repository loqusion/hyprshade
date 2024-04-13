from datetime import time

import pytest

from hyprshade.utils.time import is_time_between


class TestIsTimeBetween:
    @pytest.mark.parametrize(
        ("time_str", "start_time_str", "end_time_str", "expected"),
        [
            ("12:00", "11:00", "13:00", True),
            ("10:00", "11:00", "13:00", False),
            ("14:00", "11:00", "13:00", False),
            ("11:00", "11:00", "13:00", True),
            ("13:00", "11:00", "13:00", False),
            ("01:00", "20:00", "02:00", True),
            ("23:00", "20:00", "02:00", True),
            ("12:00", "20:00", "02:00", False),
        ],
    )
    def test(
        self, time_str: str, start_time_str: str, end_time_str: str, expected: bool
    ):
        t = time.fromisoformat(time_str)
        start_time = time.fromisoformat(start_time_str)
        end_time = time.fromisoformat(end_time_str)

        assert is_time_between(t, start_time, end_time) == expected

    def test_start_time_end_time_equal(self):
        with pytest.raises(AssertionError):
            is_time_between(time(11, 0), time(12, 0), time(12, 0))
