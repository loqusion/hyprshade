# Packaging

The following are requirements for a working installation of Hyprshade:

- Python 3.11+
- Dependencies: see `pyproject.toml`'s `project.dependencies`
- Build dependencies: [PDM-Backend](https://pdm-backend.fming.dev/)

The following are also recommended:

- Using [`python-build`](https://pypa-build.readthedocs.io/en/stable/) and [`python-installer`](https://installer.pypa.io/en/stable/) for building and installation respectively
- `LICENSE` file (destination: `/usr/share/licenses/hyprshade/`)
- `examples/` directory (destination: `/usr/share/hyprshade/`)
- `shaders/` directory (destination: `/usr/share/hyprshade/`)

See [the Arch Linux PKGBUILD](https://github.com/loqusion/aur-packages/blob/master/hyprshade/PKGBUILD) for reference.
