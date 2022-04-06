import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import legs
from snowfall.common.v1alpha import models_pb2
from snowfall.junction.client_api import models, resources
from snowfall.stdlib.format import protobuf


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


class LegType(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
    ) -> responses.Response:
        leg_type_id = request.path_params["legTypeId"]
        try:
            leg_type = protobuf.slug_to_enum_value(
                models_pb2.Schedule.Type.DESCRIPTOR,
                leg_type_id,
            )
        except KeyError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.LegTypeResource.from_proto(
                    leg_type,  # type: ignore
                    request,
                ),
            ),
        )
