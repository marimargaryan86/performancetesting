import asyncio
import datetime
from typing import cast

import lagom
from dateutil import parser
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.adapter import (
    errors,
    locations,
    places,
    trip_searches,
    trips,
)
from snowfall.project.junction.service.client_api import resources
from snowfall.stdlib import sequence
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.v1alpha import models_pb2


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
    ) -> responses.Response:
        trip = await trips_client.get(request.path_params["tripId"])

        pagination = pagination_helpers.get_pagination(request)
        sequence_page = sequence.paginate(
            sequence=trip.segments,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return await messages.create_response(
            body=models.Body(
                data=[
                    resources.SegmentResource.from_proto(
                        segment=segment,
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
                cast(
                    models_pb2.Schedule.Type.ValueType,
                    protobuf.slug_to_enum_value(
                        descriptor=models_pb2.Schedule.Type.DESCRIPTOR,
                        name=leg_type,
                    ),
                )
                for leg_type in body.get("allowedSegmentTypes", [])
            ]
        except KeyError as key_err:
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
                                    coordinates=models_pb2.Coordinates(
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
                                    coordinates=models_pb2.Coordinates(
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
