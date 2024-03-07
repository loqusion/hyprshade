# Hyprshade

Front-end to Hyprland's screen shader feature

<details>
  <summary>Screenshots</summary>

### Unfiltered

![Unfiltered](./.github/assets/unfiltered.png)

### Vibrance

![Vibrance](./.github/assets/vibrance.png)

### Blue Light Filter

![Blue Light Filter](./.github/assets/blue-light-filter.png)

</details>

## Description

Hyprshade takes full advantage of Hyprland's `decoration:screen_shader` feature
by automating the process of switching screen shaders, either from a user-defined
schedule or on the fly. It can be used as a replacement[^1] for apps that adjust
the screen's color temperature such as [f.lux](https://justgetflux.com/),
[redshift](http://jonls.dk/redshift/), or [gammastep](https://gitlab.com/chinstrap/gammastep)
with `blue-light-filter`, which is installed by default.

[^1]: Gradual color shifting currently unsupported.

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

### PyPI

If your distribution isn't officially supported, you can also install directly
from [PyPI](https://pypi.org/project/hyprshade/) with pip:

```sh
pip install --user hyprshade
```

Or with [pipx](https://pypa.github.io/pipx/):

```sh
pipx install hyprshade
```

## Usage

```text
Usage: hyprshade [OPTIONS] COMMAND [ARGS]...

Commands:
  auto     Set screen shader on schedule
  current  Print current screen shader
  install  Install systemd user units
  ls       List available screen shaders
  off      Turn off screen shader
  on       Turn on screen shader
  toggle   Toggle screen shader
```

Commands which take a shader name accept either the basename:

```sh
hyprshade on blue-light-filter
```

...or a full path name:

```sh
hyprshade on ~/.config/hypr/shaders/blue-light-filter.glsl
```

If you provide the basename, Hyprshade searches in `~/.config/hypr/shaders` and `/usr/share/hyprshade`.

### Scheduling

> [!WARNING]
> For scheduling to work, `systemd --user` must have access to the environment variable
> `HYPRLAND_INSTANCE_SIGNATURE`.
>
> Add the following line to `hyprland.conf`[^2]:
>
> ```hypr
> exec-once = dbus-update-activation-environment --systemd HYPRLAND_INSTANCE_SIGNATURE
> ```
>
> [^2]: See also: [Hyprland FAQ][hyprland-faq-import-env] ([cache][hyprland-faq-import-env-cache])

[hyprland-faq-import-env]: https://wiki.hyprland.org/FAQ/#some-of-my-apps-take-a-really-long-time-to-open
[hyprland-faq-import-env-cache]: https://web.archive.org/web/20240226003306/https://wiki.hyprland.org/FAQ/#some-of-my-apps-take-a-really-long-time-to-open

To have specific shaders enabled during certain periods of the day, you can
create a config file in either `~/.config/hypr/hyprshade.toml` or `~/.config/hyprshade/config.toml`.

```toml
[[shades]]
name = "vibrance"
default = true  # shader to use during times when there is no other shader scheduled

[[shades]]
name = "blue-light-filter"
start_time = 19:00:00
end_time = 06:00:00   # optional if you have more than one shade with start_time
```

For starters, you can copy the example config:

```sh
cp /usr/share/hyprshade/examples/config.toml ~/.config/hypr/hyprshade.toml
```

After writing your config, install the systemd timer/service [user units][systemd-user-units] and enable
the timer unit:

[systemd-user-units]: https://wiki.archlinux.org/title/Systemd/User

```sh
hyprshade install
systemctl --user enable --now hyprshade.timer
```

> [!TIP]
> Run `hyprshade install` every time you make changes to `hyprshade.toml` to keep the user units in sync.

### Tips

You probably want the following line in your `hyprland.conf`:

```hypr
exec = hyprshade auto
```

This ensures that the correct shader is enabled when you log in.
