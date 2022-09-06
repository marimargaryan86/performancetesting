import datetime
from typing import Sequence

from snowfall.vendor.direct_ferries.models import base
from snowfall.vendor.direct_ferries.models.route import Route


class TimetableData(base.CamelCaseBaseModel):
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    duration_in_minutes: int


class TimeTable(base.CamelCaseBaseModel):
    timetables: Sequence[TimetableData]
    route: Route
