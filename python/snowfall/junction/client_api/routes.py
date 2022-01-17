import datetime
import uuid

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import places
from snowfall.junction.client_api import models, request_helpers, resources, trips


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
        resource_list = [
            await resources.PlaceResource.from_data_class(place, request)
            for place in (await client.find()).places
        ]

        return models.JsonApiResponse(models.Body(data=resource_list))


class TripSearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        trip_search_repository: trips.TripSearchRepository = lagom.injectable,
    ) -> responses.Response:
        trip_search_id = uuid.UUID(request.path_params["tripSearchId"])

        try:
            trip_search = await trip_search_repository.get(trip_search_id)
        except trips.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=await trips.TripSearchResource.from_data_class(
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
        trip_search_repository: trips.TripSearchRepository = lagom.injectable,
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

        trip_search = await trip_search_repository.create(
            trips.TripSearchRequest(
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
                data=await trips.TripSearchResource.from_data_class(
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
        trip_search_repository: trips.TripSearchRepository = lagom.injectable,
    ) -> responses.Response:
        trip_search_id = uuid.UUID(request.path_params["tripSearchId"])

        try:
            await trip_search_repository.get(trip_search_id)
        except trips.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    await trips.TripResource.from_data_class(
                        trip=trips.Trip(
                            identifier=uuid.UUID(
                                "9ecd1767-3f8f-4dfe-8782-5880ff89df19",
                            ),
                        ),
                    ),
                ],
            ),
        )


class Health(endpoints.HTTPEndpoint):
    async def get(self, request: requests.Request) -> responses.Response:
        return models.JsonApiResponse(models.Body(meta={"status": "ok"}))
