from typing import Sequence

import httpx
from starlette import requests, responses


def go_status_error_handler(
    request: requests.Request,
    exc: httpx.HTTPStatusError,
    go_urls: Sequence[str],
) -> responses.Response:
    if any(exc.request.url.host in go_url for go_url in go_urls):
        return responses.JSONResponse(
            exc.response.json(),
            exc.response.status_code,
        )
    raise exc
