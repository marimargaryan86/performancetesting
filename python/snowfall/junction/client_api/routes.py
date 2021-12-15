import datetime
import uuid

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import places
from snowfall.junction.client_api import journeys, models, request_helpers, resources


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


class JourneySearch(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        journey_search_repository: journeys.JourneySearchRepository = lagom.injectable,
    ) -> responses.Response:
        journey_search_id = uuid.UUID(request.path_params["journeySearchId"])

        try:
            journey_search = await journey_search_repository.get(journey_search_id)
        except journeys.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=await journeys.JourneySearchResource.from_data_class(
                    journey_search,
                    request,
                ),
            ),
        )


class JourneySearches(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        places_client: places.Client = lagom.injectable,
        journey_search_repository: journeys.JourneySearchRepository = lagom.injectable,
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

        journey_search = await journey_search_repository.create(
            journeys.JourneySearchRequest(
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
                data=await journeys.JourneySearchResource.from_data_class(
                    journey_search,
                    request,
                ),
            ),
            status.HTTP_201_CREATED,
        )


class Health(endpoints.HTTPEndpoint):
    async def get(self, request: requests.Request) -> responses.Response:
        return models.JsonApiResponse(models.Body(meta={"status": "ok"}))
