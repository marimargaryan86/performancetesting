from __future__ import annotations

import asyncio
import itertools
import types as std_types
import zoneinfo
from collections.abc import Sequence
from typing import Self

import more_itertools

from snowfall.project.junction.go.service.planner.v1alpha import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.go.service.trips import filters, orchestrator, trips
from snowfall.project.junction.go.service.trips.v1alpha import amqp_pb2, trips_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types
from snowfall.stdlib.v1 import latlng_pb2


class _TripSearchContext(object):
    def __init__(
        self,
        repository: trips.TripSearchRepository,
        message: amqp_pb2.TripSearchTask,
    ) -> None:
        self._message = message
        self._repository = repository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: std_types.TracebackType | None,
    ) -> bool:
        if exc_type:
            await self._repository.mark_as_failed(self._message.trip_search.id)

        return False


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.TripSearchTask],
        planner: planner_pb2_grpc.PlannerServiceStub,
        trip_search_repository: trips.TripSearchRepository,
        trip_repository: trips.TripRepository,
    ):
        self._consumer = consumer_obj
        self._logger = stdout.get_logger()
        self._planner = planner
        self._trip_search_repository = trip_search_repository
        self._trip_repository = trip_repository

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.TripSearchTask],
    ) -> None:
        await self._trip_search_repository.mark_as_processing(
            message.body.trip_search.id,
        )

        origins = {
            (origin.coordinates.latitude, origin.coordinates.longitude)
            for origin in message.body.trip_search.origins
        }
        destinations = {
            (destination.coordinates.latitude, destination.coordinates.longitude)
            for destination in message.body.trip_search.destinations
        }

        if not origins or not destinations:
            return

        async with _TripSearchContext(self._trip_search_repository, message.body):
            response = await self._planner.SearchJourney(
                request=planner_pb2.SearchJourneyRequest(
                    origins=[
                        latlng_pb2.LatLng(
                            latitude=origin[0],
                            longitude=origin[1],
                        )
                        for origin in origins
                    ],
                    destinations=[
                        latlng_pb2.LatLng(
                            latitude=destination[0],
                            longitude=destination[1],
                        )
                        for destination in destinations
                    ],
                    departure_after=protobuf.datetime_to_protobuf_datetime(
                        protobuf.protobuf_to_datetime(
                            message.body.trip_search.departure_after,
                        ).astimezone(
                            zoneinfo.ZoneInfo(
                                more_itertools.first(
                                    message.body.trip_search.origins,
                                ).time_zone,
                            ),
                        ),
                    ),
                    allowed_segment_types=message.body.trip_search.allowed_segment_types,
                ),
            )

            await asyncio.gather(
                self._trip_repository.add_multiple_if_missing(response.trips),
                self._trip_search_repository.add_results_from_journey_search(
                    message.body.trip_search,
                    response,
                ),
            )


class TripCandidateSearchConsumer(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.TripCandidateSearchTask],
        trip_repository: trips.TripRepository,
        trip_candidate_search_repository: trips.TripCandidateSearchRepository,
        trip_orchestrator: orchestrator.TripOrchestrator,
        offer_orchestrator: orchestrator.OfferOrchestrator,
        max_trip_length_factor: float | None = None,
    ):
        self._consumer = consumer_obj
        self._trip_repository = trip_repository
        self._trip_candidate_search_repository = trip_candidate_search_repository
        self._trip_orchestrator = trip_orchestrator
        self._offer_orchestrator = offer_orchestrator
        self._max_trip_length_factor = max_trip_length_factor
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.TripCandidateSearchTask],
    ) -> None:
        body = message.body

        try:
            reference_groups = await self._trip_orchestrator.get_trip_reference_groups(
                criteria=list(body.trip_candidate_search.criteria),
                allowed_segment_types=list(
                    body.trip_candidate_search.allowed_segment_types,
                ),
            )
        except orchestrator.CantFulfillFullTripError:
            await self._trip_candidate_search_repository.mark_as_failed(
                body.trip_candidate_search.id,
            )

            return

        await self._trip_repository.add_multiple_if_missing(
            list(itertools.chain(*reference_groups)),
        )

        journey_candidates = (
            await self._trip_orchestrator.get_journeys_from_reference_groups(
                trip_reference_groups=reference_groups,
            )
        )

        if self._max_trip_length_factor:
            journey_candidates = filters.filter_include_multimodal(
                journey_candidates=journey_candidates,
                max_trip_length_factor=self._max_trip_length_factor,
            )

        await self._create_and_save_offer_searches(
            trip_candidate_search=body.trip_candidate_search,
            trip_groups=journey_candidates.trip_groups,
        )

    async def _create_and_save_offer_searches(
        self,
        trip_candidate_search: trips_pb2.TripCandidateSearch,
        trip_groups: Sequence[orchestrator.TripGroup],
    ) -> None:
        offer_searches = await self._offer_orchestrator.offer_searches_from_trip_groups(
            trip_groups=trip_groups,
            trip_candidate_search=trip_candidate_search,
        )

        await self._trip_candidate_search_repository.add_offer_search_ids(
            trip_candidate_search_id=trip_candidate_search.id,
            offer_search_ids=[search.id for search in offer_searches],
        )
