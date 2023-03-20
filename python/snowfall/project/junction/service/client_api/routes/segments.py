import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.go.adapter import schedules, segments
from snowfall.project.junction.service.client_api import resources
from snowfall.stdlib.integration.starlette import messages, models


class Segment(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        segment_client: segments.Client = lagom.injectable,
        schedule_client: schedules.Client = lagom.injectable,
    ) -> responses.Response:
        segment = await segment_client.get(request.path_params["segmentId"])
        schedule = await schedule_client.get(segment.schedule_id)

        return await messages.create_response(
            body=models.Body(
                data=resources.SegmentResource.from_proto(segment, schedule, request),
            ),
            request=request,
        )
