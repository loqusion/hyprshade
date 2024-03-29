from pathlib import Path
from typing import Literal

from typing_extensions import Protocol

HyprshadeDirectoryName = Literal["env", "user_hypr", "user_hyprshade", "system"]


class ShaderPathFactory(Protocol):
    def __call__(
        self,
        name: str,
        directory_name: HyprshadeDirectoryName = "system",
        *,
        extension: str = "glsl",
    ) -> Path: ...
