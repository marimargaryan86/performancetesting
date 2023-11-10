import dataclasses
import datetime
from collections.abc import Iterator, Sequence

from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offers_models_pb2,
)
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.provider import segment_grouper
from snowfall.project.junction.service.providers.benerail import train_stations
from snowfall.project.junction.service.providers.benerail.v1 import amqp_pb2
from snowfall.stdlib import h3, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import date_pb2


@dataclasses.dataclass(frozen=True)
class SearchCriteria(object):
    origin: str
    destination: str
    passenger_dobs: Sequence[datetime.date]
    outbound_departure_datetime: datetime.datetime
    session_token: str


def _generate_search_criteria(
    trip_criteria: segment_grouper.TripCriteria,
    passenger_dobs: Sequence[date_pb2.Date],
    session_token: str,
) -> Iterator[amqp_pb2.SearchCriteriaTask]:
    for origin, destination in trip_criteria.get_combinations():
        hour = trip_criteria.outbound.departure.hour

        if hour % 2:
            hour = hour - 1

        task = amqp_pb2.SearchCriteriaTask(
            segments=trip_criteria.outbound.segments,
            criteria=amqp_pb2.Criteria(
                origin_id=origin,
                destination_id=destination,
                passenger_dob=passenger_dobs,
                outbound_departure_datetime=protobuf.datetime_to_protobuf_datetime(
                    trip_criteria.outbound.departure.replace(
                        hour=hour,
                        minute=0,
                        second=0,
                        microsecond=0,
                    ),
                ),
                br_session_token=session_token,
            ),
        )

        yield task


_MAX_PAX_NUMBER = 9


class CriteriaGenerator(object):
    def __init__(
        self,
        h3_mapping: h3.H3MappingRepository[train_stations.TrainStation],
    ):
        self._mapping = h3_mapping
        self._grouper = segment_grouper.SegmentGrouper(h3_mapping)

    def from_search(
        self,
        search: offers_models_pb2.TripOfferSearch,
    ) -> list[amqp_pb2.SearchCriteriaTask]:
        if len(search.passengers) > _MAX_PAX_NUMBER:
            return []

        sub_trips = self._grouper.trips_to_sub_trips(
            trips=search.trips,
            type_filter=models_pb2.Schedule.TYPE_RAIL,
        )
        tasks: list[amqp_pb2.SearchCriteriaTask] = []

        for trip_criteria in segment_grouper.generate_trip_criteria(sub_trips):
            if trip_criteria.inbound is not None:
                continue  # handle round trip as two separate one way trips

            tasks.extend(
                _generate_search_criteria(
                    trip_criteria=trip_criteria,
                    passenger_dobs=[
                        passenger.date_of_birth for passenger in search.passengers
                    ],
                    session_token=string.uuid(),
                ),
            )

        return tasks


class SearchCriteriaGenerator(object):
    def __init__(
        self,
        train_station_repository: train_stations.TrainStationRepository,
    ) -> None:
        self._train_stations = train_station_repository

    def from_search_criteria_task(
        self,
        search_task: amqp_pb2.SearchCriteriaTask,
    ) -> SearchCriteria:
        origin = self._train_stations.get_by_id(
            search_task.criteria.origin_id,
        )
        destination = self._train_stations.get_by_id(
            search_task.criteria.destination_id,
        )

        return SearchCriteria(
            origin=origin.identifier,
            destination=destination.identifier,
            passenger_dobs=[
                protobuf.protobuf_to_date(dob)
                for dob in search_task.criteria.passenger_dob
            ],
            outbound_departure_datetime=protobuf.protobuf_to_datetime(
                search_task.criteria.outbound_departure_datetime,
            ),
            session_token=search_task.criteria.br_session_token,
        )
