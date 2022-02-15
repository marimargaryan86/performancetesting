import datetime

from snowfall.format.gtfs import models


def create_datetime(
    date: datetime.date,
    delta: datetime.timedelta,
    time_zone: datetime.tzinfo,
) -> datetime.datetime:
    return_value = datetime.datetime.combine(date, datetime.datetime.min.time())
    return_value = return_value.replace(tzinfo=time_zone)

    return return_value + delta


def _append_calendars(
    row: models.Calendar,
    now_date: datetime.date,
    service_dates: dict[str, list[datetime.date]],
) -> None:
    service_dates[row.service_id] = []
    weekdays = [
        row.monday,
        row.tuesday,
        row.wednesday,
        row.thursday,
        row.friday,
        row.saturday,
        row.sunday,
    ]

    for days in range((row.end_date - row.start_date).days + 1):
        current_date = row.start_date + datetime.timedelta(days=days)

        if current_date < now_date:
            continue

        if not weekdays[current_date.weekday()]:
            continue

        service_dates[row.service_id].append(current_date)


def _append_calendar_dates(
    row: models.CalendarDate,
    now_date: datetime.date,
    service_dates: dict[str, list[datetime.date]],
) -> None:
    if row.service_id not in service_dates:
        service_dates[row.service_id] = []

    if row.date < now_date:
        return

    in_list = row.date in service_dates[row.service_id]

    if row.exception_type == 1 and not in_list:
        service_dates[row.service_id].append(row.date)
    elif row.exception_type == 2 and in_list:
        service_dates[row.service_id].remove(row.date)


def create_service_dates_map(feed: models.Feed) -> dict[str, list[datetime.date]]:
    now_date = datetime.date.today()
    service_dates: dict[str, list[datetime.date]] = {}

    for calendar in feed.calendars:
        _append_calendars(calendar, now_date, service_dates)

    for calendar_date in feed.calendar_dates:
        _append_calendar_dates(calendar_date, now_date, service_dates)

    return service_dates
