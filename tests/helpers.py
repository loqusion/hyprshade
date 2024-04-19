from freezegun import freeze_time as _freeze_time


def freeze_time(time_str: str, date_str: str = "2024-04-08"):
    return _freeze_time(f"{date_str} {time_str}")
