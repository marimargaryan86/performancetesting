import contextlib
import http
import json

import httpx


class DFError(Exception):
    """Raised when there is an DF-related issue."""


class DFServiceError(DFError):
    """Raised when the DF service is unhealthy."""


class DFTimeoutError(httpx.TimeoutException):
    """Raised when the DF service return Timeout exception."""


def get_response_error_message(response: httpx.Response) -> str:
    status = http.HTTPStatus(response.status_code)
    description = status.description

    with contextlib.suppress(json.decoder.JSONDecodeError, AttributeError):
        description = response.json().get("title", description)

    return "{0}: {1}".format(status.value, description)
