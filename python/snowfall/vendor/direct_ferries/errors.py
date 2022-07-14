import contextlib
import http
import json

import httpx


class DFError(Exception):
    """Raised when there is an DF-related issue."""


class ServiceError(DFError):
    """Raised when the DF service is unhealthy."""


def get_response_error_message(response: httpx.Response) -> str:
    status = http.HTTPStatus(response.status_code)

    with contextlib.suppress(json.decoder.JSONDecodeError, AttributeError):
        description = response.json().get("title") or status.description

    return "{0}: {1}".format(status.value, description)
