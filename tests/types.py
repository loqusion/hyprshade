from collections.abc import Callable
from pathlib import Path

ShaderPathFactory = Callable[[str], Path]
