from __future__ import annotations

import asyncio
import itertools
import types as std_types
import zoneinfo
from collections.abc import Coroutine, Sequence
from typing import Any, Self

import more_itertools

from snowfall.project.junction.go.adapter import legs as legs_adapter
from snowfall.project.junction.go.service.planner.v1 import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.go.service.trips import (
    cache,
    filters,
    orchestrator,
    trips,
)
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


def _search_journey_request(
    trip_search_task: amqp_pb2.TripSearchTask,
) -> planner_pb2.SearchJourneyRequest:
    origins = {
        (origin.coordinates.latitude, origin.coordinates.longitude)
        for origin in trip_search_task.trip_search.origins
    }
    destinations = {
        (destination.coordinates.latitude, destination.coordinates.longitude)
        for destination in trip_search_task.trip_search.destinations
    }

    origin_tz = zoneinfo.ZoneInfo(
        more_itertools.first(
            trip_search_task.trip_search.origins,
        ).time_zone,
    )

    request = planner_pb2.SearchJourneyRequest(
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
                trip_search_task.trip_search.departure_after,
            ).astimezone(origin_tz),
        ),
        departure_before=(
            protobuf.datetime_to_protobuf_datetime(
                protobuf.protobuf_to_datetime(
                    trip_search_task.trip_search.departure_before,
                ).astimezone(origin_tz),
            )
            if trip_search_task.trip_search.HasField("departure_before")
            else None
        ),
        allowed_segment_types=trip_search_task.trip_search.allowed_segment_types,
    )

    if trip_search_task.trip_search.HasField("maximum_connections"):
        request.maximum_connections = trip_search_task.trip_search.maximum_connections

    return request


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

        async with _TripSearchContext(self._trip_search_repository, message.body):
            response = await self._planner.SearchJourney(
                request=_search_journey_request(message.body),
            )

            coros: list[
                Coroutine[Any, Any, trips_pb2.TripSearch] | Coroutine[Any, Any, None]
            ] = [
                self._trip_search_repository.add_results_from_journey_search(
                    message.body.trip_search,
                    response,
                ),
            ]

            if response.trips:
                coros.append(
                    self._trip_repository.add_multiple_if_missing(response.trips),
                )

            await asyncio.gather(*coros)


def _trip_search_can_be_fulfilled(
    trip_reference_groups: Sequence[orchestrator.TripReferenceGroup],
) -> bool:
    if not trip_reference_groups:
        return False

    return all(bool(reference_group) for reference_group in trip_reference_groups)


class TripCandidateSearchConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.TripCandidateSearchTask],
        trip_repository: trips.TripRepository,
        leg_cache_repository: cache.LegCacheRepository,
        trip_metadata_repository: cache.TripMetadataRepository,
        trip_candidate_search_repository: trips.TripCandidateSearchRepository,
        trip_orchestrator: orchestrator.TripOrchestrator,
        offer_orchestrator: orchestrator.OfferOrchestrator,
        leg_adapter: legs_adapter.GrpcClient,
        max_trip_length_factor: float | None = None,
    ):
        self._consumer = consumer_obj
        self._trip_repository = trip_repository
        self._leg_cache_repository = leg_cache_repository
        self._trip_metadata_repository = trip_metadata_repository
        self._trip_candidate_search_repository = trip_candidate_search_repository
        self._trip_orchestrator = trip_orchestrator
        self._offer_orchestrator = offer_orchestrator
        self._max_trip_length_factor = max_trip_length_factor
        self._leg_adapter = leg_adapter
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(  # noqa: WPS217
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
            self._logger.exception(
                "Failed to get trips from planner",
                trip_candidate_search_id=body.trip_candidate_search.id,
            )

            return

        if not _trip_search_can_be_fulfilled(reference_groups):
            await self._trip_candidate_search_repository.mark_as_completed(
                body.trip_candidate_search.id,
            )

            return

        await self._trip_repository.add_multiple_if_missing(
            list(itertools.chain(*reference_groups)),
        )

        await self._leg_cache_repository.fetch_many(
            ids=[  # noqa: WPS224
                leg_id
                for reference_group in reference_groups
                for reference in reference_group
                for segment in reference.segments
                for leg_id in segment.leg_ids
            ],
            legs_adapter=self._leg_adapter,
        )

        if self._max_trip_length_factor:
            for idx, _group in enumerate(reference_groups[:]):
                reference_groups[idx] = await filters.filter_trip_references(
                    trip_references=reference_groups[idx],
                    trip_metadata_repository=self._trip_metadata_repository,
                    max_trip_length_factor=self._max_trip_length_factor,
                )

        await self._create_and_save_offer_searches(
            trip_candidate_search=body.trip_candidate_search,
            trip_reference_groups=reference_groups,
        )

    async def _create_and_save_offer_searches(
        self,
        trip_candidate_search: trips_pb2.TripCandidateSearch,
        trip_reference_groups: Sequence[orchestrator.TripReferenceGroup],
    ) -> None:
        offer_search_ids = (
            await self._offer_orchestrator.offer_search_ids_from_trip_groups(
                trip_reference_groups=trip_reference_groups,
                trip_candidate_search=trip_candidate_search,
            )
        )

        await self._trip_candidate_search_repository.add_offer_search_ids(
            trip_candidate_search_id=trip_candidate_search.id,
            offer_search_ids=offer_search_ids,
        )
