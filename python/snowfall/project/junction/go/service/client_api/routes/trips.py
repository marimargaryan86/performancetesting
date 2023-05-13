import asyncio
import dataclasses
import datetime
from typing import Any, Mapping, Sequence, cast

import lagom
from dateutil import parser
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.go.adapter import (
    errors,
    locations,
    places,
    schedules,
    trip_candidate_searches,
    trip_candidates,
    trip_searches,
    trips,
)
from snowfall.project.junction.go.service.client_api import resources
from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.stdlib import sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.v1alpha import latlng_pb2

_Coordinates = Mapping[str, float]
_Passengers = list[dict[str, str]]


class Trip(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: trips.Client = lagom.injectable,
    ) -> responses.Response:
        trip = await client.get(request.path_params["tripId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.TripResource.from_proto(
                    trip=trip,
                    request=request,
                ),
            ),
            request=request,
        )


class TripSegments(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        trips_client: trips.Client = lagom.injectable,
        schedules_client: schedules.Client = lagom.injectable,
    ) -> responses.Response:
        trip = await trips_client.get(request.path_params["tripId"])

        pagination = pagination_helpers.get_pagination(request)
        sequence_page = sequence.paginate(
            sequence=trip.segments,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )
        schedule_ids = list({segment.schedule_id for segment in sequence_page.sequence})
        schedules_map = {
            schedule.id: schedule
            for schedule in (
                await schedules_client.find_by_ids(schedule_ids, len(schedule_ids))
            ).schedules
        }

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.SegmentResource.from_proto(
                        segment=segment,
                        schedule=schedules_map[segment.schedule_id],
                        request=request,
                    )
                    for segment in sequence_page.sequence
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ListTripSegments",
                        tripId=request.path_params["tripId"],
                    ),
                    sequence_page.cursor,
                    pagination,
                ),
            ),
            request=request,
        )


class TripSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: trip_searches.Client = lagom.injectable,
    ) -> responses.Response:
        trip_search = await client.get(request.path_params["tripSearchId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.TripSearchResource.from_proto(
                    trip_search,
                    request,
                ),
            ),
            request=request,
        )


class TripSearches(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210,C901
        self,
        request: requests.Request,
        locations_client: locations.Client = lagom.injectable,
        places_client: places.Client = lagom.injectable,
        trip_searches_client: trip_searches.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            (origin, destination) = await asyncio.gather(
                places_client.get(body["origin"]),
                places_client.get(body["destination"]),
            )
        except errors.NotFoundError as err:
            raise exceptions.HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ) from err

        try:
            allowed_segment_types = [
                protobuf.slug_to_enum_value(
                    enum=models_pb2.Schedule.Type,
                    name=leg_type,
                )
                for leg_type in body.get("allowedSegmentTypes", [])
            ]
        except ValueError as key_err:
            raise exceptions.HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ) from key_err

        if body.get("departureAfter"):
            departure_after = parser.isoparse(body["departureAfter"])
            current_time = datetime.datetime.now(
                datetime.timezone.utc,
            ) - datetime.timedelta(minutes=1)

            if departure_after < current_time:
                raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            departure_after = datetime.datetime.now(datetime.timezone.utc)

        location_ids = {*origin.merged_ids, *destination.merged_ids}
        response = await locations_client.find(
            identifiers=list(location_ids),
            limit=len(location_ids),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.TripSearchResource.from_proto(
                    await trip_searches_client.create(
                        trip_searches.TripSearchRequest(
                            origins=[
                                models_pb2.Point(
                                    ref=origin.location.id,
                                    name=location.name,
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=location.coordinates.latitude,
                                        longitude=location.coordinates.longitude,
                                    ),
                                    time_zone=location.time_zone,
                                )
                                for location in response.locations
                                if location.id in origin.merged_ids
                            ],
                            destinations=[
                                models_pb2.Point(
                                    ref=destination.location.id,
                                    name=location.name,
                                    coordinates=latlng_pb2.LatLng(
                                        latitude=location.coordinates.latitude,
                                        longitude=location.coordinates.longitude,
                                    ),
                                    time_zone=location.time_zone,
                                )
                                for location in response.locations
                                if location.id in destination.merged_ids
                            ],
                            departure_after=departure_after,
                            maximum_connections=body.get("maximumConnections"),
                            allowed_segment_types=allowed_segment_types,
                        ),
                    ),
                    request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )


class TripsByTripSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: trip_searches.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        response = await client.list_trips_by_trip_search(
            request.path_params["tripSearchId"],
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.TripResource.from_proto(
                        trip=trip,
                        request=request,
                    )
                    for trip in response.trips
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ViewTripsByTripSearch",
                        tripSearchId=request.path_params["tripSearchId"],
                    ),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )


@dataclasses.dataclass(frozen=True)
class TripCandidateSearches(object):
    _trip_candidate_searches_client: trip_candidate_searches.Client
    _locations_client: locations.Client
    _reseller_currencies: Mapping[str, str]
    _reseller_pay_companies: Mapping[str, str]

    async def post(self, request: messages.Request) -> responses.Response:
        return await messages.create_response(
            body=models.Body(
                data=resources.TripCandidateSearchResource.from_proto(
                    trip_candidate_search=await self._trip_candidate_searches_client.create(
                        trip_candidate_search=await self._create_trip_candidate_search(
                            request,
                        ),
                    ),
                    request=request.starlette_request,
                ),
            ),
            request=request.starlette_request,
            status_code=status.HTTP_201_CREATED,
        )

    async def _create_trip_candidate_search(
        self,
        request: messages.Request,
    ) -> trip_candidate_searches.TripCandidateSearchRequest:
        try:
            allowed_segment_types = [
                protobuf.slug_to_enum_value(
                    enum=models_pb2.Schedule.Type,
                    name=leg_type,
                )
                for leg_type in cast(
                    list[str],
                    request.body.get("allowedSegmentTypes", []),
                )
            ]
        except KeyError as key_err:
            raise exceptions.HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ) from key_err

        reseller_id = request.starlette_request.user.username
        criteria = cast(
            list[dict[str, Any]],
            request.body["criteria"],
        )
        locations_per_search = await self._get_nearby_locations(criteria)

        return trip_candidate_searches.TripCandidateSearchRequest(
            passengers=[
                offer_models_pb2.Passenger(
                    date_of_birth=protobuf.date_to_protobuf(
                        datetime.date.fromisoformat(pax["dateOfBirth"]),
                    ),
                )
                for pax in cast(_Passengers, request.body["passengers"])
            ],
            criteria=[
                trips_pb2.TripCandidateSearchCriteria(
                    origin=latlng_pb2.LatLng(
                        **criteria["origin"],
                    ),
                    destination=latlng_pb2.LatLng(
                        **criteria["destination"],
                    ),
                    origins=locations_per_search[
                        (
                            criteria["origin"]["latitude"],
                            criteria["origin"]["longitude"],
                        )
                    ],
                    destinations=locations_per_search[
                        (
                            criteria["destination"]["latitude"],
                            criteria["destination"]["longitude"],
                        )
                    ],
                    departure_after=protobuf.datetime_to_protobuf_datetime(
                        parser.isoparse(criteria["departureAfter"]),
                    ),
                    maximum_connections=criteria["maximumConnections"],
                )
                for criteria in criteria
            ],
            allowed_segment_types=list(allowed_segment_types),
            reseller_id=reseller_id,
            currency_code=self._reseller_currencies.get(reseller_id),
            pay_company_id=self._reseller_pay_companies.get(reseller_id),
        )

    async def _get_nearby_locations(
        self,
        criteria: Sequence[Mapping[str, _Coordinates]],
    ) -> Mapping[tuple[float, float], Sequence[latlng_pb2.LatLng]]:
        coordinate_pairs: list[tuple[float, float]] = []

        for single_criteria in criteria:
            coordinate_pairs.append(
                (
                    single_criteria["origin"]["latitude"],
                    single_criteria["origin"]["longitude"],
                ),
            )
            coordinate_pairs.append(
                (
                    single_criteria["destination"]["latitude"],
                    single_criteria["destination"]["longitude"],
                ),
            )

        nearby_locations = await asyncio.gather(
            *[
                self._locations_client.get_nearby_locations(
                    coordinates=latlng_pb2.LatLng(
                        latitude=pair[0],
                        longitude=pair[1],
                    ),
                )
                for pair in coordinate_pairs
            ],
        )

        return {
            coordinate_pairs[index]: [
                latlng_pb2.LatLng(
                    latitude=location_object.coordinates.latitude,
                    longitude=location_object.coordinates.longitude,
                )
                for location_object in location_objects
            ]
            for index, location_objects in enumerate(nearby_locations)
        }


class TripCandidateSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: trip_candidate_searches.Client = lagom.injectable,
    ) -> responses.Response:
        trip_candidate_search = await client.get(
            request.path_params["tripCandidateSearchId"],
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.TripCandidateSearchResource.from_proto(
                    trip_candidate_search,
                    request,
                ),
            ),
            request=request,
        )


class TripCandidatesByTripCandidateSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: trip_candidates.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        response = await client.list_trip_candidates_by_trip_candidate_search(
            request.path_params["tripCandidateSearchId"],
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.OfferResource.from_proto(
                        offer=offer,
                        request=request,
                    )
                    for offer in response.offers
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for(
                        "ViewTripCandidatesByTripCandidateSearch",
                        tripCandidateSearchId=request.path_params[
                            "tripCandidateSearchId"
                        ],
                    ),
                    response.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )
