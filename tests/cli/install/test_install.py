from configparser import ConfigParser, SectionProxy
from pathlib import Path

from click.testing import CliRunner

from hyprshade.cli import cli
from tests.conftest import Isolation
from tests.types import ConfigFactory


def parse_unit(path: Path) -> dict[str, SectionProxy]:
    unit = ConfigParser()
    unit.read_string(path.read_text())
    return dict(unit.items())


def test_no_shaders(
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


def test_multiple_shaders(
    runner: CliRunner, isolation: Isolation, config_factory: ConfigFactory
):
    pass


def test_no_config(runner: CliRunner, isolation: Isolation):
    result = runner.invoke(cli, ["install"])

    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
    assert not isolation.systemd_service_path.exists()
    assert not isolation.systemd_timer_path.exists()
