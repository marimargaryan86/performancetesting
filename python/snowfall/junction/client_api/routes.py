import uuid

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.junction.client_api import models, places


class Place(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repository: places.PlaceRepository = lagom.injectable,
    ) -> responses.Response:
        place_id = uuid.UUID(request.path_params["placeId"])

        try:
            place = await repository.get(place_id)
        except places.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(data=await places.PlaceResource.from_data_class(place)),
        )


class Places(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        repository: places.PlaceRepository = lagom.injectable,
    ) -> responses.Response:
        resources = [
            await places.PlaceResource.from_data_class(place)
            for place in await repository.find()
        ]

        return models.JsonApiResponse(models.Body(data=resources))


class Health(endpoints.HTTPEndpoint):
    async def get(self, request: requests.Request) -> responses.Response:
        return models.JsonApiResponse(models.Body(meta={"status": "ok"}))
