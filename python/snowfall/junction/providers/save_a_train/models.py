import dataclasses
import datetime


@dataclasses.dataclass(frozen=True)
class SearchResultRequirement(object):
    departure_datetime: datetime.datetime
    arrival_datetime: datetime.datetime
