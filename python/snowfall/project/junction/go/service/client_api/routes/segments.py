import dataclasses

from starlette import responses

from snowfall.project.junction.go.adapter import schedules, segments
from snowfall.project.junction.go.service.client_api import resources
from snowfall.stdlib.integration.starlette import messages, models


@dataclasses.dataclass(frozen=True)
class Segments(object):
    _schedules: schedules.Client
    _segments: segments.Client

    async def view(self, request: messages.Request) -> responses.Response:
        segment = await self._segments.get(request.path_params["segmentId"])
        schedule = await self._schedules.get(segment.schedule_id)

        return await messages.create_response(
            body=models.Body(
                data=resources.SegmentResource.from_proto(
                    segment,
                    schedule,
                    request.starlette_request,
                ),
            ),
            request=request.starlette_request,
        )
