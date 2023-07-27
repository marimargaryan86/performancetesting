import asyncio
import datetime
import itertools
import zoneinfo
from collections.abc import Mapping, Sequence
from typing import NamedTuple

import timezonefinder

from snowfall.project.junction.go.adapter import legs, offer_searches
from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.service.planner.v1alpha import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.go.service.trips import trips
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.v1 import latlng_pb2

_tz_finder = timezonefinder.TimezoneFinder()

TripReferenceGroup = Sequence[models_pb2.TripReference]
TripGroup = list[models_pb2.Trip]


class JourneyCandidates(NamedTuple):
    trip_groups: list[TripGroup]


def _sort_keys(segment: models_pb2.Segment) -> tuple[int, int]:
    return (
        segment.legs[0].departure_at.seconds,
        segment.legs[0].departure_at.nanos,
    )


class CantFulfillFullTripError(Exception):
    """Failed to get one or more trip groups or got empty one."""


class TripOrchestrator(object):
    def __init__(
        self,
        planner: planner_pb2_grpc.PlannerServiceStub,
        trip_repository: trips.TripRepository,
        legs_adapter: legs.GrpcClient,
    ):
        self._planner = planner
        self._trip_repository = trip_repository
        self._legs_adapter = legs_adapter
        self._logger = stdout.get_logger()

    async def get_trip_reference_groups(
        self,
        criteria: Sequence[trips_pb2.TripCandidateSearchCriteria],
        allowed_segment_types: Sequence[models_pb2.Schedule.Type.ValueType],
    ) -> list[list[models_pb2.TripReference]]:
        journey_search_responses = await self._get_journey_search_responses(
            criteria=criteria,
            allowed_segment_types=allowed_segment_types,
        )
        trip_groups = []

        for response in journey_search_responses:
            if isinstance(response, Exception) or not response.trips:
                raise CantFulfillFullTripError()

            trip_groups.append(list(response.trips))

        return trip_groups

    async def get_journeys_from_reference_groups(
        self,
        trip_reference_groups: Sequence[TripReferenceGroup],
    ) -> JourneyCandidates:
        trip_reference_map = {
            trip.id: trip
            async for trip in await self._trip_repository.find(
                ids=[
                    reference.id
                    for reference in itertools.chain(*trip_reference_groups)
                ],
                cursor="",
            )
        }
        legs_map = await self._make_legs_map(trip_reference_map)

        return JourneyCandidates(
            trip_groups=[
                [
                    models_pb2.Trip(
                        id=reference.id,
                        segments=sorted(
                            [
                                models_pb2.Segment(
                                    id=segment.id,
                                    legs=[
                                        legs_map[leg_id] for leg_id in segment.leg_ids
                                    ],
                                )
                                for segment in trip_reference_map[reference.id].segments
                            ],
                            key=_sort_keys,
                        ),
                    )
                    for reference in reference_group
                ]
                for reference_group in trip_reference_groups
            ],
        )

    async def _make_legs_map(
        self,
        trips_map: Mapping[str, models_pb2.TripReference],
    ) -> dict[str, models_pb2.Leg]:
        segments = [segment for trip in trips_map.values() for segment in trip.segments]
        leg_ids = {leg_id for segment in segments for leg_id in segment.leg_ids}

        return {
            leg.id: leg
            for leg in (
                await self._legs_adapter.find_by_ids(
                    list(leg_ids),
                    limit=len(leg_ids),
                )
            ).legs
        }

    async def _get_journey_search_responses(
        self,
        criteria: Sequence[trips_pb2.TripCandidateSearchCriteria],
        allowed_segment_types: Sequence[models_pb2.Schedule.Type.ValueType],
    ) -> list[planner_pb2.SearchJourneyResponse | Exception]:
        tasks = []

        for criteria_obj in criteria:
            if not criteria_obj.origins or not criteria_obj.destinations:
                continue

            tasks.append(
                self._planner.SearchJourney(
                    request=planner_pb2.SearchJourneyRequest(
                        origins=[
                            latlng_pb2.LatLng(
                                latitude=origin.latitude,
                                longitude=origin.longitude,
                            )
                            for origin in criteria_obj.origins
                        ],
                        destinations=[
                            latlng_pb2.LatLng(
                                latitude=destination.latitude,
                                longitude=destination.longitude,
                            )
                            for destination in criteria_obj.destinations
                        ],
                        departure_after=protobuf.datetime_to_protobuf_datetime(
                            protobuf.protobuf_to_datetime(
                                criteria_obj.departure_after,
                            ).astimezone(
                                zoneinfo.ZoneInfo(
                                    _tz_finder.timezone_at(
                                        lat=criteria_obj.origins[0].latitude,
                                        lng=criteria_obj.origins[0].longitude,
                                    )
                                    or "",
                                ),
                            ),
                        ),
                        allowed_segment_types=allowed_segment_types,
                        maximum_connections=criteria_obj.maximum_connections,
                    ),
                ),
            )

        return await asyncio.gather(*tasks, return_exceptions=True)


_OFFER_SEARCH_LIMIT = 50


class OfferOrchestrator(object):
    def __init__(self, offer_search_adapter: offer_searches.Client) -> None:
        self._offer_search_adapter = offer_search_adapter
        self._logger = stdout.get_logger()
        self._semaphore = asyncio.Semaphore(_OFFER_SEARCH_LIMIT)

    async def offer_searches_from_trip_groups(
        self,
        trip_groups: Sequence[TripGroup],
        trip_candidate_search: trips_pb2.TripCandidateSearch,
    ) -> list[offer_models_pb2.OfferSearch]:
        coros = (
            self._create_offer_search(trip_combination, trip_candidate_search)
            for trip_combination in itertools.product(*trip_groups)
        )

        searches = await asyncio.gather(*coros, return_exceptions=True)

        offer_search_objects = []

        for search in searches:
            if isinstance(search, Exception):
                self._logger.exception(
                    "Failed to create an offer search",
                    exception=search,
                )

                continue

            offer_search_objects.append(search)

        return offer_search_objects

    async def _create_offer_search(
        self,
        trip_combination: Sequence[models_pb2.Trip],
        trip_candidate_search: trips_pb2.TripCandidateSearch,
    ) -> offer_models_pb2.OfferSearch:
        async with self._semaphore:
            return await self._offer_search_adapter.create(
                request=offer_models_pb2.OfferSearch(
                    id=string.uuid(),
                    reseller_id=trip_candidate_search.reseller_id,
                    currency_code=trip_candidate_search.currency_code,
                    pay_company_id=trip_candidate_search.pay_company_id,
                    expires_at=protobuf.datetime_to_protobuf(
                        datetime.datetime.now(tz=datetime.UTC)
                        + datetime.timedelta(hours=2),
                    ),
                    trip=offer_models_pb2.TripOfferSearch(
                        passengers=trip_candidate_search.passengers,
                        trips=trip_combination,
                        reseller_id=trip_candidate_search.reseller_id,
                    ),
                    session_token=trip_candidate_search.session_token,
                ),
            )
