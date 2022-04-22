import datetime
import itertools
from collections.abc import Iterator
from typing import Sequence

import more_itertools

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.providers.ask2go import airports, h3
from snowfall.junction.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import enums

_DAYS_IN_YEAR = 365
_ADULT_YEARS = 12
_CHILD_YEARS = 2


class CriteriaGenerator(object):
    def __init__(self, h3_mapping: h3.H3MappingRepository[airports.Airport]):
        self._mapping = h3_mapping

    def from_search_task(
        self,
        search_task: offers_pb2.TripOfferSearchTask,
    ) -> Iterator[amqp_pb2.SearchCriteriaTask]:
        number_of_types = get_passenger_types(
            passengers=search_task.search.passengers,
            date=_get_last_travel_date(search_task),
        )

        for segment in search_task.search.segments:
            first_leg = more_itertools.first(segment.legs)

            if first_leg.type != models_pb2.Schedule.TYPE_AIR:
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
                amqp_pb2.SearchCriteriaTask(
                    offer_search_id=search_task.offer_search_id,
                    segments=[segment],
                    criteria=amqp_pb2.Criteria(
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


def _get_last_travel_date(search_task: offers_pb2.TripOfferSearchTask) -> datetime.date:
    return max(
        protobuf.protobuf_to_datetime(
            more_itertools.last(segment.legs).departure_at,
        ).date()
        for segment in search_task.search.segments
    )


def get_passenger_types(
    passengers: Sequence[offers_pb2.Passenger],
    date: datetime.date,
) -> tuple[int, int, int]:
    adults = 0
    children = 0
    infants = 0

    for passenger in passengers:
        age = get_age_at_date(passenger, date)

        if age >= _ADULT_YEARS:
            adults += 1
        elif age >= _CHILD_YEARS:
            children += 1
        else:
            infants += 1

    return adults, children, infants


def get_age_at_date(passenger: offers_pb2.Passenger, date: datetime.date) -> int:
    age = date - protobuf.protobuf_to_date(passenger.date_of_birth)

    return age.days // _DAYS_IN_YEAR
