from os import path

from hyprshade.utils import hypr_config_home


def get_shaders_dir() -> str:
    config_home = hypr_config_home()
    shaders_dir = path.join(config_home, "shaders")
    if not path.isdir(shaders_dir):
        raise FileNotFoundError(f"Shaders directory {shaders_dir} does not exist")
    return path.join(config_home, "shaders")


def get_shader_path(shader_name_or_path: str) -> str:
    shader_path = shader_name_or_path
    if not path.isfile(shader_path):
        shaders_dir = get_shaders_dir()
        shader_path = path.join(shaders_dir, glsl_ext(shader_name_or_path))
        if not path.isfile(shader_path):
            raise FileNotFoundError(
                f"Shader {shader_name_or_path} does not exist; "
                f"check contents of {shaders_dir}"
            )
    return shader_path


def glsl_ext(pathname: str) -> str:
    if pathname.endswith(".glsl"):
        return pathname
    return f"{pathname}.glsl"
