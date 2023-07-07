import dataclasses

from starlette import exceptions, responses, status

from snowfall.stdlib.integration.starlette import messages, models, pagination_helpers


@dataclasses.dataclass(frozen=True)
class Users(object):
    async def view(self, request: messages.Request) -> responses.Response:
        raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

    async def list_(self, request: messages.Request) -> responses.Response:
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
