from datetime import time

from hyprshade import utils


class TestIsTimeBetween:
    def test_normal(self):
        assert utils.is_time_between(time(12, 0), time(11, 0), time(13, 0)) is True

    def test_wrapping(self):
        assert utils.is_time_between(time(1, 0), time(20, 0), time(2, 0)) is True
        assert utils.is_time_between(time(23, 0), time(20, 0), time(2, 0)) is True
