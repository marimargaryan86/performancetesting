import datetime


def normalize_duration(duration: str) -> datetime.timedelta:
    parts = duration.split(".")
    parts_len = len(parts)

    if parts_len == 1:
        days = 0
    elif parts_len == 2:
        days = int(parts[0])
    else:
        raise ValueError("{0} day part is not valid".format(duration))

    time_parts = parts[-1].split(":")

    if len(time_parts) != 3:
        raise ValueError("{0} time part is not valid".format(duration))

    return datetime.timedelta(
        days=days,
        hours=int(time_parts[0]),
        minutes=int(time_parts[1]),
        seconds=int(time_parts[2]),
    )
