import subprocess
from pathlib import Path

import pytest

from hyprshade.shader import hyprctl

pytestmark = [
    pytest.mark.requires_hyprland(),
]


def test_hyprctl(shader_path: Path):
    hyprctl.set_screen_shader(str(shader_path))
    assert hyprctl.get_screen_shader() == str(shader_path)

    hyprctl.clear_screen_shader()
    assert hyprctl.get_screen_shader() is None


@pytest.mark.usefixtures("_mock_hyprctl_invalid_json")
def test_json_error():
    with pytest.raises(RuntimeError):
        hyprctl.get_screen_shader()


@pytest.fixture()
def _mock_hyprctl_invalid_json(monkeypatch: pytest.MonkeyPatch):
    def _subprocess_run_invalid_json(args, **kwargs) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"str": "test}',
            stderr="",
        )

    monkeypatch.setattr(hyprctl.subprocess, "run", _subprocess_run_invalid_json)
