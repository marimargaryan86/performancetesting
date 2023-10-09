import asyncio
import datetime
import itertools
import zoneinfo
from collections.abc import Sequence
from typing import NamedTuple

import timezonefinder

from snowfall.project.junction.go.adapter import errors, offer_searches
from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.service.planner.v1 import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.go.service.trips import cache
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
    trip_groups: list[TripReferenceGroup]


class CantFulfillFullTripError(Exception):
    """Failed to get one or more trip groups or got empty one."""


class TripOrchestrator(object):
    def __init__(
        self,
        planner: planner_pb2_grpc.PlannerServiceStub,
    ):
        self._planner = planner
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
        trip_reference_groups = []

        for response in journey_search_responses:
            if isinstance(response, Exception):
                raise CantFulfillFullTripError()

            trip_reference_groups.append(list(response.trips))

        return trip_reference_groups

    async def _get_journey_search_responses(
        self,
        criteria: Sequence[trips_pb2.TripCandidateSearchCriteria],
        allowed_segment_types: Sequence[models_pb2.Schedule.Type.ValueType],
    ) -> list[planner_pb2.SearchJourneyResponse | Exception]:
        tasks = []

        for criteria_obj in criteria:
            if not criteria_obj.origins or not criteria_obj.destinations:
                continue

            origin_tz = zoneinfo.ZoneInfo(
                _tz_finder.timezone_at(
                    lat=criteria_obj.origins[0].latitude,
                    lng=criteria_obj.origins[0].longitude,
                )
                or "",
            )

            request = planner_pb2.SearchJourneyRequest(
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
                    ).astimezone(origin_tz),
                ),
                departure_before=(
                    protobuf.datetime_to_protobuf_datetime(
                        protobuf.protobuf_to_datetime(
                            criteria_obj.departure_before,
                        ).astimezone(origin_tz),
                    )
                    if criteria_obj.HasField("departure_before")
                    else None
                ),
                allowed_segment_types=allowed_segment_types,
            )

            if criteria_obj.HasField("maximum_connections"):
                request.maximum_connections = criteria_obj.maximum_connections

            tasks.append(
                self._planner.SearchJourney(
                    request=request,
                ),
            )

        return await asyncio.gather(*tasks, return_exceptions=True)


_OFFER_SEARCH_LIMIT = 50


class OfferOrchestrator(object):
    def __init__(
        self,
        offer_search_adapter: offer_searches.Client,
        leg_cache_repository: cache.LegCacheRepository,
    ) -> None:
        self._offer_search_adapter = offer_search_adapter
        self._leg_cache_repo = leg_cache_repository
        self._logger = stdout.get_logger()
        self._semaphore = asyncio.Semaphore(_OFFER_SEARCH_LIMIT)

    async def offer_search_ids_from_trip_groups(
        self,
        trip_reference_groups: Sequence[TripReferenceGroup],
        trip_candidate_search: trips_pb2.TripCandidateSearch,
    ) -> list[str]:
        coros = (
            self._create_offer_search(trip_reference_combination, trip_candidate_search)
            for trip_reference_combination in itertools.product(*trip_reference_groups)
        )

        search_ids = await asyncio.gather(*coros, return_exceptions=True)

        offer_search_ids = []

        for search_id in search_ids:
            if isinstance(search_id, Exception):
                if not isinstance(search_id, errors.ServiceUnavailableError):
                    self._logger.exception(
                        "Failed to create an offer search",
                        exception=search_id,
                    )

                continue

            offer_search_ids.append(search_id)

        return offer_search_ids

    async def _create_offer_search(
        self,
        trip_reference_combination: Sequence[models_pb2.TripReference],
        trip_candidate_search: trips_pb2.TripCandidateSearch,
    ) -> str:
        async with self._semaphore:
            return await self._offer_search_adapter.create_get_id(
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
                        trips=await self._trips_from_trip_references(
                            trip_reference_combination,
                        ),
                        reseller_id=trip_candidate_search.reseller_id,
                    ),
                    session_token=trip_candidate_search.session_token,
                ),
            )

    async def _trips_from_trip_references(
        self,
        trip_references: Sequence[models_pb2.TripReference],
    ) -> list[models_pb2.Trip]:
        leg_ids = [  # noqa: WPS224
            leg_id
            for trip_reference in trip_references
            for segment in trip_reference.segments
            for leg_id in segment.leg_ids
        ]
        leg_map = {
            leg_cache_obj.id: leg_cache_obj.leg
            async for leg_cache_obj in await self._leg_cache_repo.find(leg_ids)
        }

        not_found_legs = set(leg_ids) - set(leg_map.keys())

        if not_found_legs:
            self._logger.warning("Legs not found in cache", legs=not_found_legs)

        return [
            models_pb2.Trip(
                id=trip_reference.id,
                segments=[
                    models_pb2.Segment(
                        id=segment_ref.id,
                        legs=[leg_map[leg_id] for leg_id in segment_ref.leg_ids],
                    )
                    for segment_ref in trip_reference.segments
                ],
            )
            for trip_reference in trip_references
        ]
