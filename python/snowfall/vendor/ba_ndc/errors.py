import contextlib
import http
import json

import httpx


class BaNdcError(Exception):
    """Raised when there is an BA NDC-related issue."""


class ServiceError(BaNdcError):
    """Raised when the BA NDC service is unhealthy."""


class AsyncTimeOutError(BaNdcError):
    """Raised when the async function exceeds the timeout duration."""


def get_response_error_message(response: httpx.Response) -> str:
    status = http.HTTPStatus(response.status_code)
    description = None

    with contextlib.suppress(json.decoder.JSONDecodeError, AttributeError):
        response_json = response.json()

        if response_json:
            description = response_json.get("detail")

    return "{0}: {1}".format(status.value, description or status.description)
