from collections.abc import Sequence
from datetime import UTC, date, datetime

from snowfall.project.junction.rocket.service.api.air.models import Passenger

_adult = 18
_infant = 2


def passengers_to_fake_user_ids(passengers: Sequence[Passenger]) -> list[int]:
    today = datetime.now(tz=UTC).date()
    counters = [0, 0, 0]

    def wrapper(born: date) -> int:
        had_yearly_birthday = (today.month, today.day) >= (born.month, born.day)
        age = today.year - born.year - (not had_yearly_birthday)
        if age < _infant:
            return 2
        if age < _adult:
            return 1
        return 0

    ret = []

    for pa in passengers:
        type_ = wrapper(pa.date_of_birth)
        counters[type_] += 1
        ret.append(-(counters[type_] * 10 + type_))

    return ret
