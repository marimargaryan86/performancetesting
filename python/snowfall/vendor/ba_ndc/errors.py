import http

import httpx


class BaNdcError(Exception):
    """Raised when there is an BA NDC-related issue."""


class ServiceError(BaNdcError):
    """Raised when the BA NDC service is unhealthy."""


def get_response_error_message(response: httpx.Response) -> str:
    status = http.HTTPStatus(response.status_code)
    response_json = response.json()
    return "{0}: {1}".format(status.value, response_json.get("detail"))
