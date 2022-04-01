import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import legs
from snowfall.junction.client_api import models, resources


class Leg(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: legs.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            leg = await client.get(request.path_params["legId"])
        except legs.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.LegResource.from_proto(leg, request),
            ),
        )
