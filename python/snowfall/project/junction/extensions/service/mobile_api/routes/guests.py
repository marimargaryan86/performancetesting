import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.extensions.service.mobile_api import (
    jwt_generator,
    repository,
    resources,
)
from snowfall.project.junction.extensions.service.mobile_api.v1alpha.models_pb2 import (
    Guest as GuestModel,
)
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import models
from snowfall.stdlib.integration.starlette import models as stdlib_models
from snowfall.stdlib.integration.starlette import request_helpers


class Guests(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        guests_repository: repository.GuestsRepository = lagom.injectable,
    ) -> responses.Response:
        guest = await guests_repository.insert(
            GuestModel(
                id=string.uuid(),
            ),
        )
        return stdlib_models.JsonApiResponse(
            stdlib_models.Body(
                data=resources.GuestResource.from_proto(guest),
            ),
            status.HTTP_201_CREATED,
        )


class Session(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        guests_repository: repository.GuestsRepository = lagom.injectable,
        jwt_gen: jwt_generator.JwtGenerator = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        guest = await guests_repository.find_by_id(body["guest"])
        if not guest:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)
        token = jwt_gen.encode(guest.id)

        return models.JsonApiResponse(
            models.Body(
                data=models.Resource(
                    id=token,
                    type="guest-sessions",
                    attributes={},
                    relationships={
                        "guest": {
                            "data": {
                                "id": body["guest"],
                                "type": "guests",
                            },
                        },
                    },
                ),
            ),
        )
