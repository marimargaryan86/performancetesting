import dataclasses
from typing import Any, Mapping, Optional

from starlette import background as starlette_background
from starlette import requests

from snowfall.stdlib.integration.starlette import includes, models, pagination_helpers


@dataclasses.dataclass(frozen=True)
class Request(object):
    pagination: pagination_helpers.Pagination
    path_params: Mapping[str, str]
    starlette_request: requests.Request  # @deprecated


async def create_response(
    body: models.Body,
    request: requests.Request,
    status_code: int = 200,
    headers: Optional[Mapping[str, Any]] = None,
    background: Optional[starlette_background.BackgroundTask] = None,
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
