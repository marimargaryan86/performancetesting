import dataclasses
import datetime
from collections.abc import Sequence


@dataclasses.dataclass(frozen=True)
class Criteria:
    search_id: str
    origin: str
    destination: str
    # The departure must be at this time or after (inclusive).
    outbound_departure_after: datetime.datetime
    # The departure must be strictly before this time (exclusive).
    outbound_departure_before: datetime.datetime
    passenger_dobs: Sequence[datetime.date]
