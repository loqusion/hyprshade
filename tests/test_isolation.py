import os

from hyprshade.shader.core import Shader
from tests.conftest import Isolation


def test_isolation(isolation: Isolation):
    import sysconfig

    assert os.environ.get("XDG_CONFIG_HOME") == str(isolation.config_dir)
    assert os.environ.get("XDG_STATE_HOME") == str(isolation.state_dir)
    assert os.environ.get(Shader.dirs.ENV_VAR_NAME) == str(isolation.hyprshade_env_dir)
    assert sysconfig.get_path("data") == str(isolation.usr_dir)
    assert os.getcwd() == isolation.cwd
