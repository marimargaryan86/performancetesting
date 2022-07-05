import datetime
import itertools
from collections.abc import Iterator
from typing import Sequence

import more_itertools

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2, models_pb2
from snowfall.project.junction.service.providers.ask2go import airports
from snowfall.project.junction.service.providers.ask2go.v1alpha import (
    amqp_pb2 as provider_amqp_pb2,
)
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2 as common_models_pb2
from snowfall.vendor.ask2go import enums
from snowfall.vendor.ask2go.models import common

_ADULT_YEARS = 12
_CHILD_YEARS = 2


class CriteriaGenerator(object):
    def __init__(self, h3_mapping: h3.H3MappingRepository[airports.Airport]):
        self._mapping = h3_mapping

    def from_search_task(
        self,
        search_task: amqp_pb2.TripOfferSearchTask,
    ) -> Iterator[provider_amqp_pb2.SearchCriteriaTask]:
        number_of_types = get_num_of_passenger_types(
            passengers=search_task.search.passengers,
            date=_get_last_travel_date(search_task),
        )

        for segment in search_task.search.segments:
            first_leg = more_itertools.first(segment.legs)

            if first_leg.type != common_models_pb2.Schedule.TYPE_AIR:
                continue

            origins = self._mapping.find_mapped_values(
                coordinates=first_leg.origin.coordinates,
                neighbour_search_radius=1,
            )
            destinations = self._mapping.find_mapped_values(
                coordinates=more_itertools.last(segment.legs).destination.coordinates,
                neighbour_search_radius=1,
            )

            yield from (
                provider_amqp_pb2.SearchCriteriaTask(
                    offer_search_id=search_task.offer_search_id,
                    segments=[segment],
                    criteria=provider_amqp_pb2.Criteria(
                        origin_iata=pair[0].iata,
                        destination_iata=pair[1].iata,
                        outbound=protobuf.datetime_to_protobuf_datetime(
                            protobuf.protobuf_to_datetime(
                                first_leg.departure_at,
                            ).astimezone(pair[0].timezone),
                        ),
                        cabin_class=enums.AirCabinClassType.any_.value,
                        adults=number_of_types[0],
                        children=number_of_types[1],
                        infants=number_of_types[2],
                    ),
                )
                for pair in itertools.product(origins, destinations)
            )


def _get_last_travel_date(
    search_task: amqp_pb2.TripOfferSearchTask,
) -> datetime.date:
    return max(
        protobuf.protobuf_to_datetime(
            more_itertools.last(segment.legs).departure_at,
        ).date()
        for segment in search_task.search.segments
    )


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
) -> tuple[int, int, int]:
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

    return adults, children, infants


def _get_age_at_date(birth_date: datetime.date, travel_date: datetime.date) -> int:
    year_difference = travel_date.year - birth_date.year

    return year_difference - (
        (travel_date.month, travel_date.day) < (birth_date.month, birth_date.day)
    )
