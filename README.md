# Hyprshade

Frontend to Hyprland's screen shader feature

## Features

- Switch shaders on/off by name
- Toggle shader on/off
- Automate shader scheduling with systemd

## Installation

### Arch Linux

Use your favorite AUR helper (e.g. [paru](https://github.com/Morganamilo/paru)):

```sh
paru -S hyprshade
```

Or manually:

```sh
sudo pacman -S --needed base-devel
git clone https://aur.archlinux.org/hyprshade.git
cd hyprshade
makepkg -si
```

### Other

If your distribution isn't officially supported, you can also install directly
from [PyPI](https://pypi.org/project/hyprshade/) with pip:

```sh
pip install --user hyprshade
```

Or with [pipx](https://pypa.github.io/pipx/):

```sh
pipx install hyprshade
```
