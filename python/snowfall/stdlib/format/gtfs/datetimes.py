import contextlib
import datetime
from typing import AsyncIterable

from snowfall.stdlib.format.gtfs import models


def create_datetime(
    date: datetime.date,
    delta: datetime.timedelta,
    time_zone: datetime.tzinfo,
) -> datetime.datetime:
    return_value = datetime.datetime.combine(date, datetime.datetime.min.time())
    return_value = return_value.replace(tzinfo=time_zone)

    return return_value + delta


async def _yield_calendars(
    rows: AsyncIterable[models.Calendar],
    now_date: datetime.date,
) -> AsyncIterable[datetime.date]:
    async for row in rows:
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

            if current_date < now_date or not weekdays[current_date.weekday()]:
                continue

            yield current_date


async def calculate_serviceable_dates(
    calendars: AsyncIterable[models.Calendar],
    calendar_dates: AsyncIterable[models.CalendarDate],
) -> set[datetime.date]:
    now_date = datetime.date.today()
    service_dates: set[datetime.date] = {
        date async for date in _yield_calendars(calendars, now_date)
    }

    async for row in calendar_dates:
        if row.date < now_date:
            continue

        if row.exception_type == 1:
            service_dates.add(row.date)
        elif row.exception_type == 2:
            with contextlib.suppress(KeyError):
                service_dates.remove(row.date)

    return service_dates
