import datetime

import lagom
from dateutil import parser
from furl import furl
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import places, segments, trip_searches, trips
from snowfall.junction.client_api import models, request_helpers, resources

_PAGE_LIMIT = "page[limit]"
_PAGE_CURSOR = "page[cursor]"


class Trip(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: trips.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            trip = await client.get(request.path_params["tripId"])
        except trips.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

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
        segments_client: segments.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            trip = await trips_client.get(request.path_params["tripId"])
        except trips.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        cursor = request.query_params[_PAGE_CURSOR]
        limit = int(request.query_params[_PAGE_LIMIT])

        sequence_page = await request_helpers.sequence_paginator(
            sequence=trip.segments,
            limit=limit,
            cursor=int(cursor) if cursor else 0,
        )

        next_url = furl(
            request.url_for(
                "ListTripSegments",
                tripId=request.path_params["tripId"],
            ),
        )
        next_url.args[_PAGE_CURSOR] = sequence_page.next_page_token
        next_url.args[_PAGE_LIMIT] = limit

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.SegmentResource.from_proto(
                        segment=segment,
                        request=request,
                    )
                    for segment in sequence_page.sequence
                ],
                links={
                    "next": next_url.url,
                },
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
                data=resources.TripSearchResource.from_proto(
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
        cursor = request.query_params[_PAGE_CURSOR]
        limit = int(request.query_params[_PAGE_LIMIT])

        try:
            response = await client.list_trips_by_trip_search(
                request.path_params["tripSearchId"],
                cursor=cursor,
                limit=limit,
            )
        except trip_searches.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        next_url = furl(
            request.url_for(
                "ViewTripsByTripSearch",
                tripSearchId=request.path_params["tripSearchId"],
            ),
        )
        next_url.args[_PAGE_CURSOR] = response.next_page_token
        next_url.args[_PAGE_LIMIT] = limit

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.TripResource.from_proto(
                        trip=trip,
                        request=request,
                    )
                    for trip in response.trips
                ],
                links={
                    "next": next_url.url,
                },
            ),
        )
