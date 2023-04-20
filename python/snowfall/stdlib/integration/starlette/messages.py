import dataclasses
from typing import Mapping

from starlette import background as starlette_background
from starlette import requests

from snowfall.stdlib import types
from snowfall.stdlib.integration.starlette import includes, models, pagination_helpers


@dataclasses.dataclass(frozen=True)
class Request(object):
    body: types.PrimitiveMapping
    pagination: pagination_helpers.Pagination
    path_params: Mapping[str, str]
    query_params: types.PrimitiveMapping
    starlette_request: requests.Request  # @deprecated


async def create_response(
    body: models.Body,
    request: requests.Request,
    status_code: int = 200,
    headers: Mapping[str, str] | None = None,
    background: starlette_background.BackgroundTask | None = None,
) -> models.JsonApiResponse:
    included = await includes.resolve_includes(body, request)

    if included:
        body.included = included

    return models.JsonApiResponse(
        body=body,
        status_code=status_code,
        headers=headers,
        background=background,
    )
