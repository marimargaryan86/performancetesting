import datetime

import lagom
from dateutil import parser
from starlette import endpoints, exceptions, requests, responses, status

from snowfall import fixtures
from snowfall.adapter import places, trip_searches
from snowfall.common.v1alpha import models_pb2
from snowfall.junction.client_api import models, request_helpers, resources


class Trip(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:

        if request.path_params["tripId"] == fixtures.NOT_FOUND:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=await resources.TripResource.from_proto(
                    trip=models_pb2.TripReference(
                        id=request.path_params["tripId"],
                    ),
                    request=request,
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
        except trip_searches.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=await resources.TripSearchResource.from_proto(
                    trip_search,
                    request,
                ),
            ),
        )


class TripSearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        places_client: places.Client = lagom.injectable,
        trip_searches_client: trip_searches.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            origin = await places_client.get(body["origin"])
        except places.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            destination = await places_client.get(body["destination"])
        except places.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

        if body.get("departureAfter"):
            departure_after = parser.isoparse(body["departureAfter"])
        else:
            departure_after = datetime.datetime.now(datetime.timezone.utc)

        trip_search = await trip_searches_client.create(
            trip_searches.TripSearchRequest(
                origin=origin,
                destination=destination,
                departure_after=departure_after,
            ),
        )

        return models.JsonApiResponse(
            models.Body(
                data=await resources.TripSearchResource.from_proto(
                    trip_search,
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
        try:
            trips = await client.list_trips_by_trip_search(
                request.path_params["tripSearchId"],
            )
        except trip_searches.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    await resources.TripResource.from_proto(
                        trip=trip,
                        request=request,
                    )
                    for trip in trips
                ],
            ),
        )
