import os
from os import path


def xdg_config_home():
    config_home = os.getenv("XDG_CONFIG_HOME")
    if config_home is None:
        home = os.getenv("HOME")
        if home is None:
            raise ValueError("$HOME environment variable is not set")
        config_home = path.join(home, ".config")
    return config_home
