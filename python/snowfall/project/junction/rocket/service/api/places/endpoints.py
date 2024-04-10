import datetime

import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.rocket.service.api import errors
from snowfall.project.junction.rocket.service.api.places.models import (
    places as place_models,
)
from snowfall.project.junction.rocket.service.places.v1alpha import (
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib.integration.starlette import messages, models


class GetPlace(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def get(
        self,
        request: requests.Request,
        places: places_pb2_grpc.PlacesServiceStub = lagom.injectable,
        grpc_timeout: datetime.timedelta = lagom.injectable,
    ) -> responses.Response:
        path_params = request.path_params
        place_id = path_params["placeId"]

        response = await places.GetPlace(
            places_pb2.GetPlaceRequest(id=place_id),
            timeout=grpc_timeout.total_seconds(),
        )

        return await messages.create_response(
            body=models.Body(
                data=place_models.PlacesResource.from_proto(
                    response.place,
                    request,
                ),
            ),
            request=request,
        )
