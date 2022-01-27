import datetime
import uuid

import lagom
from furl import furl
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import places, trip_searches, trips
from snowfall.junction.client_api import models, request_helpers, resources

_DEFAULT_PAGE_LIMIT = 20


class Place(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        place_id = uuid.UUID(request.path_params["placeId"])

        try:
            place = await client.get(place_id)
        except places.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=await resources.PlaceResource.from_data_class(place, request),
            ),
        )


class Places(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: places.Client = lagom.injectable,
    ) -> responses.Response:
        cursor = request.query_params.get("page[cursor]")
        limit = int(request.query_params.get("page[limit]", _DEFAULT_PAGE_LIMIT))
        response = await client.find(limit=limit, cursor=cursor)
        resource_list = [
            await resources.PlaceResource.from_data_class(place, request)
            for place in response.places
        ]

        next_url = furl(request.url_for("ListPlaces"))
        next_url.args["page[cursor]"] = response.next_page_token
        next_url.args["page[limit]"] = limit

        return models.JsonApiResponse(
            models.Body(
                data=resource_list,
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
        trip_search_id = uuid.UUID(request.path_params["tripSearchId"])

        try:
            trip_search = await client.get(trip_search_id)
        except trip_searches.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=await resources.TripSearchResource.from_data_class(
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
        client: trip_searches.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            origin = await places_client.get(body["origin"])
        except places.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        try:
            destination = await places_client.get(body["destination"])
        except places.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        trip_search = await client.create(
            trip_searches.TripSearchRequest(
                origin=origin,
                destination=destination,
                departure_after=body.get("departureAfter")
                or datetime.datetime.now(
                    datetime.timezone.utc,
                ),
            ),
        )

        return models.JsonApiResponse(
            models.Body(
                data=await resources.TripSearchResource.from_data_class(
                    trip_search,
                    request,
                ),
            ),
            status.HTTP_201_CREATED,
        )


class Trips(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: trip_searches.Client = lagom.injectable,
    ) -> responses.Response:
        trip_search_id = uuid.UUID(request.path_params["tripSearchId"])

        try:
            await client.get(trip_search_id)
        except trip_searches.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    await resources.TripResource.from_data_class(
                        trip=trips.Trip(
                            identifier=uuid.UUID(
                                "9ecd1767-3f8f-4dfe-8782-5880ff89df19",
                            ),
                            expires_at=datetime.datetime.now(
                                datetime.timezone.utc,
                            )
                            + datetime.timedelta(days=1),
                        ),
                    ),
                ],
            ),
        )


class Health(endpoints.HTTPEndpoint):
    async def get(self, request: requests.Request) -> responses.Response:
        return models.JsonApiResponse(models.Body(meta={"status": "pass"}))
