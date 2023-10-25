import datetime
import itertools
from collections.abc import Iterator, Mapping, Sequence

import more_itertools

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.provider import airports, segment_grouper
from snowfall.project.junction.service.providers.ask2go.v1 import (
    amqp_pb2 as provider_amqp_pb2,
)
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go import enums

_ADULT_YEARS = 12
_CHILD_YEARS = 2


class CriteriaGenerator(object):
    def __init__(
        self,
        h3_mapping: h3.H3MappingRepository[airports.Airport],
        reseller_id_affiliate_id_map: Mapping[str, str],
        min_lower_bound: datetime.timedelta | None = None,
    ):
        self._mapping = h3_mapping
        self._reseller_id_affiliate_id_map = reseller_id_affiliate_id_map
        self._grouper = segment_grouper.SegmentGrouper(h3_mapping, min_lower_bound)

    def from_search(
        self,
        search: offer_models_pb2.TripOfferSearch,
    ) -> list[provider_amqp_pb2.SearchCriteriaTask]:
        number_of_types = get_num_of_passenger_types(
            passenger_dobs=[
                protobuf.protobuf_to_date(passenger.date_of_birth)
                for passenger in search.passengers
            ],
            date_of_travel=_get_last_travel_date(search),
        )
        sub_trips = self._grouper.trips_to_sub_trips(
            trips=search.trips,
            type_filter=models_pb2.Schedule.TYPE_AIR,
        )
        tasks: list[provider_amqp_pb2.SearchCriteriaTask] = []

        for trip_criteria in segment_grouper.generate_trip_criteria(sub_trips):
            tasks.extend(
                _generate_search_criteria(
                    trip_criteria=trip_criteria,
                    number_of_types=number_of_types,
                    affiliate_id=self._reseller_id_affiliate_id_map.get(
                        search.reseller_id,
                    ),
                ),
            )

        return tasks


def _generate_search_criteria(
    trip_criteria: segment_grouper.TripCriteria,
    number_of_types: tuple[int, int, int],
    affiliate_id: str | None = None,
) -> Iterator[provider_amqp_pb2.SearchCriteriaTask]:
    for origin, destination in trip_criteria.get_combinations():
        task = provider_amqp_pb2.SearchCriteriaTask(
            segments=trip_criteria.outbound.segments,
            criteria=provider_amqp_pb2.Criteria(
                origin_iata=origin,
                destination_iata=destination,
                outbound_departure=protobuf.datetime_to_protobuf_datetime(
                    trip_criteria.outbound.departure,
                ),
                cabin_class=enums.AirCabinClassType.any_.value,
                adults=number_of_types[0],
                children=number_of_types[1],
                infants=number_of_types[2],
                affiliate_id=affiliate_id or "",
            ),
        )

        if trip_criteria.inbound:
            task.segments.extend(
                trip_criteria.inbound.segments,
            )
            task.criteria.inbound_departure.CopyFrom(
                protobuf.datetime_to_protobuf_datetime(
                    trip_criteria.inbound.departure,
                ),
            )

        yield task


def _get_last_travel_date(
    search: offer_models_pb2.TripOfferSearch,
) -> datetime.date:
    segments = itertools.chain(*[tr.segments for tr in search.trips])

    return max(
        protobuf.protobuf_to_date(more_itertools.last(segment.legs).departure_at)
        for segment in segments
    )


def get_passenger_type(
    date_of_birth: datetime.date,
    date_of_travel: datetime.date,
) -> enums.PassengerType:
    age = _get_age_at_date(date_of_birth, date_of_travel)

    if age >= _ADULT_YEARS:
        return enums.PassengerType.adult

    if age >= _CHILD_YEARS:
        return enums.PassengerType.child

    return enums.PassengerType.infant


def get_num_of_passenger_types(
    passenger_dobs: Sequence[datetime.date],
    date_of_travel: datetime.date,
) -> tuple[int, int, int]:
    adults = 0
    children = 0
    infants = 0

    for date_of_birth in passenger_dobs:
        pax_type = get_passenger_type(
            date_of_birth=date_of_birth,
            date_of_travel=date_of_travel,
        )

        if pax_type == enums.PassengerType.adult:
            adults += 1
        elif pax_type == enums.PassengerType.child:
            children += 1
        else:
            infants += 1

    return adults, children, infants


def _get_age_at_date(birth_date: datetime.date, travel_date: datetime.date) -> int:
    year_difference = travel_date.year - birth_date.year

    return year_difference - (
        (travel_date.month, travel_date.day) < (birth_date.month, birth_date.day)
    )
