import asyncio
import datetime

import lagom
from dateutil import parser
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.adapter import locations, trip_searches, trips
from snowfall.project.junction.service.client_api import resources
from snowfall.stdlib import sequence
from snowfall.stdlib.integration.starlette import (
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
        try:
            trip = await client.get(request.path_params["tripId"])
        except trips.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripResource.from_proto(
                    trip=trip,
                    request=request,
                ),
            ),
        )


class TripSegments(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        trips_client: trips.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            trip = await trips_client.get(request.path_params["tripId"])
        except trips.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        pagination = pagination_helpers.get_pagination(request)
        sequence_page = sequence.paginate(
            sequence=trip.segments,
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        return models.JsonApiResponse(
            models.Body(
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
        )


class TripSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: trip_searches.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            trip_search = await client.get(request.path_params["tripSearchId"])
        except trip_searches.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripSearchResource.from_proto(
                    trip_search,
                    request,
                ),
            ),
        )


class TripSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        locations_client: locations.Client = lagom.injectable,
        trip_searches_client: trip_searches.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            (origin, destination) = await asyncio.gather(
                locations_client.get(body["origin"]),
                locations_client.get(body["destination"]),
            )
        except locations.NotFoundError as err:
            raise exceptions.HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ) from err

        if body.get("departureAfter"):
            departure_after = parser.isoparse(body["departureAfter"])
            current_time = datetime.datetime.now(
                datetime.timezone.utc,
            ) - datetime.timedelta(minutes=1)

            if departure_after < current_time:
                raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            departure_after = datetime.datetime.now(datetime.timezone.utc)

        return models.JsonApiResponse(
            models.Body(
                data=resources.TripSearchResource.from_proto(
                    await trip_searches_client.create(
                        trip_searches.TripSearchRequest(
                            origin=models_pb2.Point(
                                ref=origin.id,
                                name=origin.name,
                                coordinates=models_pb2.Coordinates(
                                    latitude=origin.coordinates.latitude,
                                    longitude=origin.coordinates.longitude,
                                ),
                                time_zone=origin.time_zone,
                            ),
                            destination=models_pb2.Point(
                                ref=destination.id,
                                name=destination.name,
                                coordinates=models_pb2.Coordinates(
                                    latitude=destination.coordinates.latitude,
                                    longitude=destination.coordinates.longitude,
                                ),
                                time_zone=destination.time_zone,
                            ),
                            departure_after=departure_after,
                        ),
                    ),
                    request,
                ),
            ),
            status.HTTP_201_CREATED,
        )


class TripsByTripSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: trip_searches.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)

        try:
            response = await client.list_trips_by_trip_search(
                request.path_params["tripSearchId"],
                cursor=pagination.cursor,
                limit=pagination.limit,
            )
        except trip_searches.NotFoundError as err:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND) from err

        return models.JsonApiResponse(
            models.Body(
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
        )
