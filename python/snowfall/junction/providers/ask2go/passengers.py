import datetime
from typing import NamedTuple, Sequence

from snowfall.junction.offers.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go.models import common

_ADULT_YEARS = 12
_CHILD_YEARS = 2


class PassengerTypes(NamedTuple):
    adults: int
    children: int
    infants: int


def get_passenger_type(
    date_of_birth: datetime.date,
    date_of_travel: datetime.date,
) -> common.PassengerType:
    age = _get_age_at_date(date_of_birth, date_of_travel)

    if age >= _ADULT_YEARS:
        return common.PassengerType.adult

    if age >= _CHILD_YEARS:
        return common.PassengerType.child

    return common.PassengerType.infant


def get_num_of_passenger_types(
    passengers: Sequence[models_pb2.Passenger],
    date: datetime.date,
) -> PassengerTypes:
    adults = 0
    children = 0
    infants = 0

    for passenger in passengers:
        pax_type = get_passenger_type(
            protobuf.protobuf_to_date(passenger.date_of_birth),
            date,
        )

        if pax_type == common.PassengerType.adult:
            adults += 1
        elif pax_type == common.PassengerType.child:
            children += 1
        else:
            infants += 1

    return PassengerTypes(adults, children, infants)


def _get_age_at_date(birth_date: datetime.date, travel_date: datetime.date) -> int:
    year_difference = travel_date.year - birth_date.year

    return year_difference - (
        (travel_date.month, travel_date.day) < (birth_date.month, birth_date.day)
    )
