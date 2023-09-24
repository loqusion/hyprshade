import pytest

pytestmark = [
    pytest.mark.requires_hyprland(),
    pytest.mark.usefixtures("_save_screen_shader"),
]
