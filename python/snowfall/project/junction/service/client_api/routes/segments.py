import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.adapter import segments
from snowfall.project.junction.service.client_api import resources
from snowfall.stdlib.integration.starlette import messages, models


class Segment(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: segments.Client = lagom.injectable,
    ) -> responses.Response:
        segment = await client.get(request.path_params["segmentId"])

        return await messages.create_response(
            body=models.Body(
                data=resources.SegmentResource.from_proto(segment, request),
            ),
            request=request,
        )
