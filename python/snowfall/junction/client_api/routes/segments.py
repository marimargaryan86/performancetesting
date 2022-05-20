import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import segments
from snowfall.junction.client_api import resources
from snowfall.stdlib.integration.starlette import models


class Segment(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: segments.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            segment = await client.get(request.path_params["segmentId"])
        except segments.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.SegmentResource.from_proto(segment, request),
            ),
        )
