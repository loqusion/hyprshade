from datetime import datetime, time

import pytest

from hyprshade.config.model import ConfigError
from hyprshade.config.schedule import Schedule
from tests.helpers import freeze_time
from tests.types import ConfigFactory


class TestScheduledShader:
    @pytest.mark.parametrize(
        ("time_str", "expected"),
        [
            ("00:00:00", "default"),
            ("12:00:00", "default"),
            ("19:59:30", "default"),
            ("20:00:00", "test1"),
            ("20:30:00", "test1"),
            ("20:59:30", "test1"),
            ("21:00:00", "test2"),
            ("22:00:00", "test2"),
            ("22:59:30", "test2"),
            ("23:00:00", "test3"),
            ("23:30:00", "test3"),
            ("23:59:30", "test3"),
        ],
    )
    def test(self, time_str: str, expected: str, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test1",
                        "start_time": time.fromisoformat("20:00"),
                        "end_time": time.fromisoformat("21:00"),
                    },
                    {
                        "name": "test2",
                        "start_time": time.fromisoformat("21:00"),
                    },
                    {
                        "name": "test3",
                        "start_time": time.fromisoformat("23:00"),
                        "end_time": time.fromisoformat("00:00"),
                    },
                    {
                        "name": "default",
                        "default": True,
                    },
                ]
            }
        )
        schedule = Schedule(config_factory.get_config())

        with freeze_time(time_str):
            shader = schedule.scheduled_shader(datetime.now().time())
            assert shader is not None
            assert shader.name == expected

    def test_no_default(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test",
                        "start_time": time.fromisoformat("20:00"),
                        "end_time": time.fromisoformat("21:00"),
                    }
                ]
            }
        )
        schedule = Schedule(config_factory.get_config())

        with freeze_time("12:00"):
            shader = schedule.scheduled_shader(datetime.now().time())
            assert shader is None

    def test_empty_config(self, config_factory: ConfigFactory):
        config_factory.write({})
        schedule = Schedule(config_factory.get_config())

        with freeze_time("12:00"):
            shader = schedule.scheduled_shader(datetime.now().time())
            assert shader is None


class TestEventTimes:
    def test(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test1",
                        "start_time": time.fromisoformat("20:00"),
                        "end_time": time.fromisoformat("21:00"),
                    },
                    {
                        "name": "test2",
                        "start_time": time.fromisoformat("21:00"),
                        "end_time": time.fromisoformat("22:00"),
                    },
                    {
                        "name": "test3",
                        "start_time": time.fromisoformat("23:00"),
                    },
                    {
                        "name": "default",
                        "default": True,
                    },
                ]
            }
        )
        schedule = Schedule(config_factory.get_config())

        assert list(schedule.event_times()) == [
            time.fromisoformat("20:00"),
            time.fromisoformat("21:00"),
            time.fromisoformat("22:00"),
            time.fromisoformat("23:00"),
        ]

    def test_empty_config(self, config_factory: ConfigFactory):
        config_factory.write({})
        schedule = Schedule(config_factory.get_config())

        assert list(schedule.event_times()) == []


class TestDefaultShader:
    def test(self, config_factory: ConfigFactory):
        config_factory.write({"shaders": [{"name": "default", "default": True}]})
        schedule = Schedule(config_factory.get_config())

        shader = schedule.default_shader
        assert shader is not None
        assert shader.name == "default"

    def test_no_default(self, config_factory: ConfigFactory):
        config_factory.write({"shaders": [{"name": "test"}]})
        schedule = Schedule(config_factory.get_config())

        assert schedule.default_shader is None

    def test_multiple_default(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "default1",
                        "default": True,
                    },
                    {
                        "name": "default2",
                        "default": True,
                    },
                ]
            }
        )
        schedule = Schedule(config_factory.get_config())

        with pytest.raises(ConfigError):
            _ = schedule.default_shader


class TestResolvedEntries:
    def test(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test1",
                        "start_time": time.fromisoformat("20:00"),
                        "end_time": time.fromisoformat("21:00"),
                    },
                    {
                        "name": "test2",
                        "start_time": time.fromisoformat("21:00"),
                        "end_time": time.fromisoformat("22:00"),
                    },
                    {
                        "name": "test3",
                        "start_time": time.fromisoformat("23:00"),
                    },
                    {
                        "name": "default",
                        "default": True,
                    },
                ]
            }
        )
        schedule = Schedule(config_factory.get_config())

        entries = list(schedule._resolved_entries())
        assert len(entries) == 3

        assert entries[0].name == "test1"
        assert entries[0].start_time == time.fromisoformat("20:00")
        assert entries[0].end_time == time.fromisoformat("21:00")

        assert entries[1].name == "test2"
        assert entries[1].start_time == time.fromisoformat("21:00")
        assert entries[1].end_time == time.fromisoformat("22:00")

        assert entries[2].name == "test3"
        assert entries[2].start_time == time.fromisoformat("23:00")
        assert entries[2].end_time == time.fromisoformat("20:00")

    def test_empty_config(self, config_factory: ConfigFactory):
        config_factory.write({})
        schedule = Schedule(config_factory.get_config())

        assert list(schedule._resolved_entries()) == []


class TestEntries:
    def test(self, config_factory: ConfigFactory):
        config_factory.write(
            {
                "shaders": [
                    {
                        "name": "test1",
                        "start_time": time.fromisoformat("20:00"),
                        "end_time": time.fromisoformat("21:00"),
                    },
                    {
                        "name": "test2",
                        "start_time": time.fromisoformat("21:00"),
                        "end_time": time.fromisoformat("22:00"),
                    },
                    {
                        "name": "test3",
                        "start_time": time.fromisoformat("23:00"),
                    },
                    {
                        "name": "default",
                        "default": True,
                    },
                ]
            }
        )
        schedule = Schedule(config_factory.get_config())

        entries = schedule._entries()
        assert len(entries) == 3

        assert entries[0].name == "test1"
        assert entries[0].start_time == time.fromisoformat("20:00")
        assert entries[0].end_time == time.fromisoformat("21:00")

        assert entries[1].name == "test2"
        assert entries[1].start_time == time.fromisoformat("21:00")
        assert entries[1].end_time == time.fromisoformat("22:00")

        assert entries[2].name == "test3"
        assert entries[2].start_time == time.fromisoformat("23:00")
        assert entries[2].end_time is None

    def test_empty_config(self, config_factory: ConfigFactory):
        config_factory.write({})
        schedule = Schedule(config_factory.get_config())

        assert list(schedule._entries()) == []
