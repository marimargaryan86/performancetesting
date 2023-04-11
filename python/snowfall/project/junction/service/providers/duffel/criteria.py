import datetime
import itertools
from typing import Iterator, Sequence

import more_itertools

from snowfall.project.junction.go.service.offers.v1alpha import amqp_pb2
from snowfall.project.junction.provider import airports, segment_grouper
from snowfall.project.junction.service.providers.duffel.v1alpha import (
    amqp_pb2 as provider_amqp_pb2,
)
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2


class CriteriaGenerator(object):
    def __init__(
        self,
        h3_mapping: h3.H3MappingRepository[airports.Airport],
    ):
        self._mapping = h3_mapping
        self._grouper = segment_grouper.SegmentGrouper(h3_mapping)

    def from_search_task(
        self,
        search_task: amqp_pb2.TripOfferSearchTask,
    ) -> list[provider_amqp_pb2.SearchCriteriaTask]:
        last_travel_date = _get_last_travel_date(search_task)
        passenger_ages = [
            _get_age_at_date(
                protobuf.protobuf_to_date(passenger.date_of_birth),
                last_travel_date,
            )
            for passenger in search_task.search.passengers
        ]
        sub_trips = self._grouper.trips_to_sub_trips(
            trips=search_task.search.trips,
            type_filter=models_pb2.Schedule.TYPE_AIR,
        )
        tasks: list[provider_amqp_pb2.SearchCriteriaTask] = []

        for trip_criteria in segment_grouper.generate_trip_criteria(sub_trips):
            tasks.extend(
                _generate_search_criteria(
                    search_task=search_task,
                    trip_criteria=trip_criteria,
                    passenger_ages=passenger_ages,
                ),
            )

        return tasks


def _get_last_travel_date(
    search_task: amqp_pb2.TripOfferSearchTask,
) -> datetime.date:
    segments = itertools.chain(*[tr.segments for tr in search_task.search.trips])

    return max(
        protobuf.protobuf_to_datetime(
            more_itertools.last(segment.legs).departure_at,
        ).date()
        for segment in segments
    )


def _generate_search_criteria(
    search_task: amqp_pb2.TripOfferSearchTask,
    trip_criteria: segment_grouper.TripCriteria,
    passenger_ages: Sequence[int],
) -> Iterator[provider_amqp_pb2.SearchCriteriaTask]:
    for origin, destination in trip_criteria.get_combinations():
        task = provider_amqp_pb2.SearchCriteriaTask(
            offer_search_id=search_task.offer_search_id,
            segments=trip_criteria.outbound.segments,
            criteria=provider_amqp_pb2.Criteria(
                origin_iata=origin,
                destination_iata=destination,
                outbound_departure=protobuf.datetime_to_protobuf_datetime(
                    trip_criteria.outbound.departure,
                ),
                passenger_ages=passenger_ages,
            ),
            session_token=search_task.session_token,
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


def _get_age_at_date(birth_date: datetime.date, travel_date: datetime.date) -> int:
    year_difference = travel_date.year - birth_date.year

    return year_difference - (
        (travel_date.month, travel_date.day) < (birth_date.month, birth_date.day)
    )
