import datetime
from typing import Sequence

import pydantic

from snowfall.vendor.direct_ferries.models import base
from snowfall.vendor.direct_ferries.models.route import Route


class Timetable(base.CamelCaseBaseModel):
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    duration_in_minutes: int


class OperatorTimetable(base.CamelCaseBaseModel):
    operator_id: int
    timetables: Sequence[Timetable]


class TimetableData(base.CamelCaseBaseModel):
    operator_timetables: Sequence[OperatorTimetable]


class TimetableResponse(base.CamelCaseBaseModel):
    timetable_data: TimetableData = pydantic.Field(..., alias="data")
    route: Route
