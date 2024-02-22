from collections.abc import Mapping, Sequence
from typing import Any

import httpx
from starlette import requests, responses

from snowfall.stdlib.integration.starlette import models


def go_status_error_handler(
    request: requests.Request,
    exc: httpx.HTTPStatusError,
    go_urls: Sequence[str],
) -> responses.Response:
    if any(exc.request.url.host in go_url for go_url in go_urls):
        return responses.JSONResponse(
            exc.response.json(),
            exc.response.status_code,
            media_type=models.JsonApiResponse.media_type,
        )
    raise exc


def get_includes_from_response(
    response: Mapping[str, Any],
) -> list[models.Resource]:
    if not response.get("included"):
        return []

    return [models.Resource(**include) for include in response.get("included", [])]
