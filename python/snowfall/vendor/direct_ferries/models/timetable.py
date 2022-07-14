import datetime
from typing import Sequence

from snowfall.vendor.direct_ferries.models import base


class TimetableData(base.CamelCaseBaseModel):
    departure: datetime.datetime
    arrival: datetime.datetime
    duration: int


class TimeTable(base.CamelCaseBaseModel):
    timetables: Sequence[datetime.datetime]
