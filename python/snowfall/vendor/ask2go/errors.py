from __future__ import annotations

import contextlib
import dataclasses
import http
import inspect
import json

import httpx


@dataclasses.dataclass(frozen=True)
class RequestMetaData:
    method: str
    url: str
    body: str | None

    @classmethod
    def from_error(cls, error: httpx.HTTPError) -> RequestMetaData:
        return cls(
            method=error.request.method,
            url=str(error.request.url),
            body=error.request.content.decode() or None,
        )


@dataclasses.dataclass(frozen=True)
class ResponseMetaData:
    status_code: int
    body: str | None

    @classmethod
    def from_error(cls, error: httpx.HTTPStatusError) -> ResponseMetaData:
        return cls(
            status_code=error.response.status_code,
            body=error.response.content.decode() or None,
        )


class Ask2GoError(Exception):
    """Raised when there is an Ask2Go-related issue."""


class RequestError(Ask2GoError):
    """Raised when the request against Ask2Go fails."""

    def __init__(
        self,
        message: str,
        request: RequestMetaData,
    ):
        super().__init__(message)
        self.request = request

    @classmethod
    def from_error(cls, error: httpx.RequestError) -> RequestError:
        return cls(
            message=inspect.getdoc(error) or "Request failed",
            request=RequestMetaData.from_error(error),
        )


class HttpStatusError(Ask2GoError):
    """Raised when the response from Ask2Go is not 2XX."""

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


class DateError(Ask2GoError):
    """Raised when Inbound date is lower than outbound date."""


class TimeOutError(RequestError):
    """Raised when a request times out."""


class AsyncTimeOutError(Ask2GoError):
    """Raised when the async function exceeds the timeout duration."""


def _get_response_error_message(response: httpx.Response) -> str:
    status = http.HTTPStatus(response.status_code)
    description = status.description

    with contextlib.suppress(json.decoder.JSONDecodeError, AttributeError):
        description = response.json().get("title") or status.description

    return "{0}: {1}".format(status.value, description)
