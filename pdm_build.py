from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pathlib import Path

    from pdm.backend.hooks import Context


FILE_NAMES: Final = {
    "bash": "hyprshade.bash",
    "fish": "hyprshade.fish",
    "zsh": "_hyprshade",
}


def generate_completions(shell: str, target_dir: Path, root_dir: Path):
    completion_script = root_dir / "completion.sh"
    pipe = subprocess.run(
        ["bash", str(completion_script), shell],
        capture_output=True,
        text=True,
        check=True,
    )

    file_name = FILE_NAMES.get(shell, None)
    if file_name is None:
        raise ValueError(f"Unknown shell: {shell}")

    with open(target_dir / file_name, "w") as f:
        f.write(pipe.stdout)


def pdm_build_initialize(context: Context):
    build_dir = context.ensure_build_dir()
    completions_dir = build_dir / "assets" / "completions"
    completions_dir.mkdir(parents=True, exist_ok=True)

    for shell in ["bash", "zsh", "fish"]:
        generate_completions(shell, completions_dir, context.root)
