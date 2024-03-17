from __future__ import annotations

import os


def user_config_dir(appname: str) -> str:
    path = os.environ.get("XDG_CONFIG_HOME", "")
    if not path.strip():
        path = os.path.expanduser("~/.config")
    return os.path.join(path, appname)
