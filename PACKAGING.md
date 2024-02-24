# Packaging

The following are requirements for a working installation of Hyprshade:

- Python 3.11+
- Dependencies: see `pyproject.toml`'s `project.dependencies`
- Build dependencies: [Hatchling](https://hatch.pypa.io/latest/) (not required
  if you install from wheel)

The following are also recommended:

- Using [`python-build`](https://pypa-build.readthedocs.io/en/stable/) and
  [`python-installer`](https://installer.pypa.io/en/stable/) for building and
  installation respectively
  - When using a non-standard build or installation method, make sure the [data
    directory](https://peps.python.org/pep-0427/#the-data-directory) is installed
    properly to ensure the default shaders are available.
- `LICENSE` file (destination: `/usr/share/licenses/hyprshade/`)
- `examples/` directory (destination: `/usr/share/hyprshade/`)
- Completions (see [Click documentation](https://click.palletsprojects.com/en/8.1.x/shell-completion/)
  for how to generate them)

See [the Arch Linux PKGBUILD](https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=hyprshade)
for reference.
