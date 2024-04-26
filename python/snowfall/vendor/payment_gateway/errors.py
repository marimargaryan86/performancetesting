from __future__ import annotations

import contextlib
import dataclasses
import http
import json

import httpx


class PayGwError(Exception):
    """Raised when there is an PayGw-related issue."""


@dataclasses.dataclass(frozen=True)
class RequestMetaData:
    method: str
    url: str
    body: str | None

    @classmethod
    def from_error(cls, error: httpx.HTTPError) -> RequestMetaData:
        return cls.from_request(error.request)

    @classmethod
    def from_request(cls, request: httpx.Request) -> RequestMetaData:
        return cls(
            method=request.method,
            url=str(request.url),
            body=request.content.decode() or None,
        )


@dataclasses.dataclass(frozen=True)
class ResponseMetaData:
    status_code: int
    body: str | None

    @classmethod
    def from_error(cls, error: httpx.HTTPStatusError) -> ResponseMetaData:
        return cls.from_response(error.response)

    @classmethod
    def from_response(cls, response: httpx.Response) -> ResponseMetaData:
        return cls(
            status_code=response.status_code,
            body=response.content.decode() or None,
        )


def _get_response_error_message(response: httpx.Response) -> str:
    status = http.HTTPStatus(response.status_code)
    description = status.description

    with contextlib.suppress(json.decoder.JSONDecodeError, AttributeError):
        description = response.json().get("title") or status.description

    return "{0}: {1}".format(status.value, description)


class HttpStatusError(PayGwError):
    """Raised when the response from payment gateway is not 2XX."""

    def __init__(
        self,
        message: str,
        request: RequestMetaData,
        response: ResponseMetaData,
    ):
        super().__init__(message)
        self.request = request
        self.response = response

    @classmethod
    def from_error(cls, error: httpx.HTTPStatusError) -> HttpStatusError:
        return cls(
            message=_get_response_error_message(error.response),
            request=RequestMetaData.from_error(error),
            response=ResponseMetaData.from_error(error),
        )
