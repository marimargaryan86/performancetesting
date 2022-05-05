import dataclasses
import datetime


@dataclasses.dataclass(frozen=True)
class GeneralSearchResultRequirement(object):
    departure_datetime: datetime.datetime
    arrival_datetime: datetime.datetime
