import re
from collections.abc import Sequence
from configparser import SectionProxy
from datetime import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from hyprshade.cli import cli
from hyprshade.cli.install import write_systemd_user_unit
from tests.conftest import Isolation
from tests.helpers import SystemdUnitParser
from tests.types import ConfigFactory


def parse_unit(path: Path) -> dict[str, SectionProxy]:
    unit = SystemdUnitParser()
    unit.read_string(path.read_text())
    return dict(unit.items())


def test_no_entries(
    runner: CliRunner, isolation: Isolation, config_factory: ConfigFactory
):
    config_factory.write({"shaders": []})
    result = runner.invoke(cli, ["install"])

    assert result.exit_code == 0

    assert isolation.systemd_service_path.exists()
    service_config = parse_unit(isolation.systemd_service_path)
    assert isinstance(service_config["Service"]["ExecStart"], str)

    assert isolation.systemd_timer_path.exists()
    timer_config = parse_unit(isolation.systemd_timer_path)
    assert timer_config["Timer"].get("OnCalendar") is None


def test_one_entry(
    runner: CliRunner, isolation: Isolation, config_factory: ConfigFactory
):
    config_factory.write(
        {"shaders": [{"name": "foo", "start_time": time.fromisoformat("12:00")}]}
    )
    result = runner.invoke(cli, ["install"])

    assert result.exit_code == 0

    assert isolation.systemd_service_path.exists()
    service_config = parse_unit(isolation.systemd_service_path)
    assert isinstance(service_config["Service"]["ExecStart"], str)

    assert isolation.systemd_timer_path.exists()
    timer_config = parse_unit(isolation.systemd_timer_path)
    assert isinstance(timer_config["Timer"]["OnCalendar"], str)
    assert re.search(r"12:00:00", timer_config["Timer"]["OnCalendar"])


def test_two_entries(
    runner: CliRunner, isolation: Isolation, config_factory: ConfigFactory
):
    config_factory.write(
        {
            "shaders": [
                {
                    "name": "foo",
                    "start_time": time.fromisoformat("12:00"),
                    "end_time": time.fromisoformat("13:00"),
                }
            ]
        }
    )
    result = runner.invoke(cli, ["install"])

    assert result.exit_code == 0

    assert isolation.systemd_service_path.exists()
    service_config = parse_unit(isolation.systemd_service_path)
    assert isinstance(service_config["Service"]["ExecStart"], str)

    assert isolation.systemd_timer_path.exists()
    timer_config = parse_unit(isolation.systemd_timer_path)
    assert isinstance(timer_config["Timer"]["OnCalendar"], Sequence)
    assert len(timer_config["Timer"]["OnCalendar"]) == 2
    assert re.search(r"12:00:00", timer_config["Timer"]["OnCalendar"][0])
    assert re.search(r"13:00:00", timer_config["Timer"]["OnCalendar"][1])


def test_multiple_entries(
    runner: CliRunner, isolation: Isolation, config_factory: ConfigFactory
):
    config_factory.write(
        {
            "shaders": [
                {
                    "name": "foo",
                    "start_time": time.fromisoformat("12:00"),
                    "end_time": time.fromisoformat("13:00"),
                },
                {
                    "name": "bar",
                    "start_time": time.fromisoformat("13:00"),
                    "end_time": time.fromisoformat("14:00"),
                },
                {
                    "name": "baz",
                    "start_time": time.fromisoformat("14:30"),
                },
                {
                    "name": "qux",
                    "start_time": time.fromisoformat("15:00"),
                },
            ]
        }
    )
    result = runner.invoke(cli, ["install"])

    assert result.exit_code == 0

    assert isolation.systemd_service_path.exists()
    service_config = parse_unit(isolation.systemd_service_path)
    assert isinstance(service_config["Service"]["ExecStart"], str)

    assert isolation.systemd_timer_path.exists()
    timer_config = parse_unit(isolation.systemd_timer_path)
    assert isinstance(timer_config["Timer"]["OnCalendar"], Sequence)
    assert len(timer_config["Timer"]["OnCalendar"]) == 5
    assert re.search(r"12:00:00", timer_config["Timer"]["OnCalendar"][0])
    assert re.search(r"13:00:00", timer_config["Timer"]["OnCalendar"][1])
    assert re.search(r"14:00:00", timer_config["Timer"]["OnCalendar"][2])
    assert re.search(r"14:30:00", timer_config["Timer"]["OnCalendar"][3])
    assert re.search(r"15:00:00", timer_config["Timer"]["OnCalendar"][4])


def test_option_enable(
    runner: CliRunner,
    isolation: Isolation,
    config_factory: ConfigFactory,
    monkeypatch: pytest.MonkeyPatch,
):
    from hyprshade.cli.install import subprocess

    class SubprocessRunMock:
        def __init__(self):
            self.count = 0

        def __call__(self, *args, **kwargs):
            self.count += 1

    subprocess_run_mock = SubprocessRunMock()
    monkeypatch.setattr(subprocess, "run", subprocess_run_mock)

    config_factory.write({"shaders": []})
    result = runner.invoke(cli, ["install", "--enable"])

    assert result.exit_code == 0
    assert subprocess_run_mock.count == 1


def test_no_config(runner: CliRunner, isolation: Isolation):
    result = runner.invoke(cli, ["install"])

    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
    assert not isolation.systemd_service_path.exists()
    assert not isolation.systemd_timer_path.exists()


def test_write_systemd_user_unit(isolation: Isolation):
    write_systemd_user_unit("service", "foo")
    assert (
        isolation.config_dir / "systemd/user/hyprshade.service"
    ).read_text() == "foo"

    write_systemd_user_unit("timer", "bar")
    assert (isolation.config_dir / "systemd/user/hyprshade.timer").read_text() == "bar"
