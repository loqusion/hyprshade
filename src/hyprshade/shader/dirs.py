from __future__ import annotations

import os
from typing import Final

from more_itertools import first_true

from hyprshade.utils.xdg import user_config_dir


class ShaderDirs:
    ENV_VAR_NAME: Final = "HYPRSHADE_SHADERS_DIR"
    SYSTEM_DIR: Final = "/usr/share/hyprshade/shaders"

    @staticmethod
    def env() -> str:
        return os.path.expanduser(
            os.path.expandvars(os.path.expandvars("$" + ShaderDirs.ENV_VAR_NAME))
        )

    @staticmethod
    def user_hypr() -> str:
        return os.path.join(user_config_dir("hypr"), "shaders")

    @staticmethod
    def user_hyprshade() -> str:
        return os.path.join(user_config_dir("hyprshade"), "shaders")

    @staticmethod
    def system() -> str:
        import sysconfig

        return first_true(
            [os.path.join(sysconfig.get_path("data"), "share", "hyprshade", "shaders")],
            pred=os.path.exists,
            default=ShaderDirs.SYSTEM_DIR,
        )

    @staticmethod
    def all() -> list[str]:
        return [
            x
            for x in [
                ShaderDirs.env(),
                ShaderDirs.user_hypr(),
                ShaderDirs.user_hyprshade(),
                ShaderDirs.system(),
            ]
            if os.path.exists(x)
        ]
