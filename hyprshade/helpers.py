from os import path

from .constants import SHADER_DIRS


def resolve_shader_path(shader_name_or_path: str) -> str:
    shader_path = shader_name_or_path
    if not path.isfile(shader_path):
        for shaders_dir in SHADER_DIRS:
            shader_path = path.join(shaders_dir, glsl_ext(shader_name_or_path))
            if path.isfile(shader_path):
                break

    if not path.isfile(shader_path):
        raise FileNotFoundError(f"Shader {shader_name_or_path} does not exist")

    return shader_path


def glsl_ext(pathname: str) -> str:
    if pathname.endswith(".glsl"):
        return pathname
    return f"{pathname}.glsl"
