from datetime import time

import pytest

from hyprshade.config.core import Config


def test_example_config(request: pytest.FixtureRequest):
    config = Config(str(request.session.config.rootpath / "examples/config.toml"))
    config.model.parse_fields()

    assert config.model.raw_data == {
        "shades": [
            {
                "name": "vibrance",
                "start_time": None,
                "end_time": None,
                "default": True,
                "config": None,
            },
            {
                "name": "blue-light-filter",
                "start_time": time(19, 0, 0),
                "end_time": time(6, 0, 0),
                "gradual_shift_duration": 10,
                "default": False,
                "config": None,
            },
            {
                "name": "color-filter",
                "start_time": None,
                "end_time": None,
                "default": False,
                "config": {
                    "type": "protanopia",
                    "intensity": 1.0,
                },
            },
        ]
    }
