from glob import iglob
from os import path

from more_itertools import first

from .constants import SHADER_DIRS


def resolve_shader_path(shader_name_or_path: str) -> str:
    if path.isfile(shader_name_or_path):
        return shader_name_or_path

    for shaders_dir in SHADER_DIRS:
        shader_path = first(
            iglob(f"{shader_name_or_path}*", root_dir=shaders_dir), None
        )
        if shader_path is not None:
            return path.join(shaders_dir, shader_path)

    raise FileNotFoundError(f"Shader {shader_name_or_path} does not exist")
