import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import schedules
from snowfall.junction.client_api import models, resources


class Leg(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: schedules.Client = lagom.injectable,
    ) -> responses.Response:
        origin_id = request.path_params["legId"]

        try:
            origin = await client.get_stop(origin_id)
        except schedules.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        try:
            destination = await client.get_next_stop(origin_id)
        except schedules.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.LegResource.from_proto(
                    origin,
                    destination,
                    request,
                ),
            ),
        )
