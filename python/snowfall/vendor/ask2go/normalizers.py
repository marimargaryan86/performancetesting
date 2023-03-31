import datetime


def normalize_duration(duration: str) -> datetime.timedelta:
    parts = duration.split(".")
    parts_len = len(parts)

    if parts_len < 1 or parts_len > 2:
        raise ValueError("{0} is not a valid duration".format(duration))

    days = 0

    if parts_len == 2:
        try:
            days = int(parts[0])
        except ValueError as err:
            raise ValueError("{0} is not a valid duration".format(duration)) from err

    time_parts = parts[-1].split(":")

    if len(time_parts) != 3:
        raise ValueError("{0} is not a valid duration".format(duration))

    return datetime.timedelta(
        days=days,
        hours=int(time_parts[0]),
        minutes=int(time_parts[1]),
        seconds=int(time_parts[2]),
    )
