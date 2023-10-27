import dataclasses

from starlette import exceptions, responses, status

from snowfall.project.junction.hub.service.hub_api.permissions import check_permission
from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers


@dataclasses.dataclass(frozen=True)
class Users(object):
    async def view(self, request: messages.Request) -> responses.Response:
        check_permission("user.view", request.starlette_request.user.permissions)

        raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

    async def list_(self, request: messages.Request) -> responses.Response:
        check_permission("user.view", request.starlette_request.user.permissions)

        return models.JsonApiResponse(
            models.Body(
                data=[],
                links=pagination_helpers.get_next_url(
                    request.starlette_request.url_for("ListUsers"),
                    "",
                    request.pagination,
                ),
            ),
        )


class UserInformation(object):
    async def get(self, request: messages.Request) -> responses.Response:
        return responses.JSONResponse(
            {"permissions": request.starlette_request.user.permissions},
        )
