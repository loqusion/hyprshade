import copy
from datetime import time
from os import path
from typing import Any, TypeVar, cast

import tomllib

from hyprshade.utils import hyprshade_config_home, is_time_between

K = TypeVar("K")
V = TypeVar("V")


class ShadeConfig:
    name: str
    default: bool
    start_time: time | None = None
    end_time: time | None = None

    def __init__(self, shade_config: dict):
        try:
            self._shade_config = shade_config
            self.name = shade_config["name"]
            self.default = shade_config.get("default", False)
            if not self.default:
                self.start_time = shade_config["start_time"]
                self.end_time = shade_config.get("end_time")
        except KeyError as e:
            raise ValueError(f"Missing key {e} in shade config") from e

    def __repr__(self) -> str:
        return (
            f"ShadeConfig(name={self.name}, default={self.default}, "
            f"start_time={self.start_time}, end_time={self.end_time})"
        )


class Config:
    shades: list[ShadeConfig]
    default: ShadeConfig | None = None

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = Config.get_path()
        config = Config.load(config_path)
        shades_list: list = config["shades"]
        self.shades = list(map(ShadeConfig, shades_list))
        self._coerce()

    def _coerce(self):
        """Performs config file validation and deduplicates time entries.

        If a shade is marked as default, it is set as the default shade.
        If a shade has an end time in the time range of another shade,
        the end time is removed.

        If more than one shade is marked as default, or if there are multiple
        shades with the same start time, an error is raised.
        """

        start_times: dict[time, ShadeConfig] = {}
        shades_mut = copy.deepcopy(self.shades)
        for shade, shade_mut in zip(self.shades, shades_mut, strict=True):
            if shade.default:
                self._set_default(shade)
                continue

            if shade.start_time in start_times:
                raise ValueError(
                    f"Multiple shades with start time {shade.start_time}: "
                    f"'{shade.name}' and '{start_times[shade.start_time].name}'"
                )

            if shade.start_time is not None:
                start_times[shade.start_time] = shade_mut

            if shade.end_time is not None:

                def other_shade_has_time_range(s: ShadeConfig) -> bool:
                    return (
                        s.start_time is not None
                        and s.end_time is not None
                        and s.name != shade.name  # noqa: B023
                    )

                if shade.start_time is not None:
                    for cshade in filter(other_shade_has_time_range, self.shades):
                        if is_time_between(
                            cast(time, cshade.end_time),
                            shade.start_time,
                            shade.end_time,
                        ):
                            cshade_mut = next(
                                s for s in shades_mut if s.name == cshade.name
                            )
                            cshade_mut.end_time = None
                            break

                for cshade in filter(other_shade_has_time_range, self.shades):
                    if is_time_between(
                        shade.end_time,
                        cast(time, cshade.start_time),
                        cast(time, cshade.end_time),
                    ):
                        shade_mut.end_time = None
                        break

        self.shades = shades_mut

    @staticmethod
    def load(config_path: str) -> dict[str, Any]:
        with open(config_path, "rb") as f:
            return tomllib.load(f)

    @staticmethod
    def get_path() -> str:
        return path.join(hyprshade_config_home(), "config.toml")

    def _set_default(self, shade: ShadeConfig):
        if self.default is not None:
            raise ValueError(
                f"Multiple default shades: '{self.default.name}' and '{shade.name}'\n"
                "Please set only one shade as default."
            )
        self.default = shade
