from __future__ import annotations

import contextlib
import dataclasses
import http
import inspect
import json

import httpx

from snowfall.vendor.junction_one.models.base import Response


class JunctionOneError(Exception):
    """Raised when there is an JunctionOne-related issue."""


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


class EmptyDataError(JunctionOneError):
    def __init__(self) -> None:
        super().__init__("Empty Data Response")


class ProtocolError(JunctionOneError):
    """Raised when the request against JunctionOne fails on the protocol level."""

    def __init__(
        self,
        message: str | None,
        body: str | None,
        code: int | None,
        request: RequestMetaData,
        response: ResponseMetaData,
    ):
        super().__init__(message)

    @classmethod
    def from_request(
        cls,
        message: str,
        error_response: Response,
        response: httpx.Response,
    ) -> ProtocolError:
        return cls(
            message=message,
            body=repr(error_response.data),
            code=error_response.code,
            request=RequestMetaData.from_request(response.request),
            response=ResponseMetaData.from_response(response),
        )

    @classmethod
    def from_error(
        cls,
        error_response: Response,
        response: httpx.Response,
    ) -> ProtocolError:
        return cls(
            message=error_response.error,
            body=repr(error_response.data),
            code=error_response.code,
            request=RequestMetaData.from_request(response.request),
            response=ResponseMetaData.from_response(response),
        )


class RequestError(JunctionOneError):
    """Raised when the request against JunctionOne fails."""

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


def _get_response_error_message(response: httpx.Response) -> str:
    status = http.HTTPStatus(response.status_code)
    description = status.description

    with contextlib.suppress(json.decoder.JSONDecodeError, AttributeError):
        description = response.json().get("title") or status.description

    return "{0}: {1}".format(status.value, description)


class HttpStatusError(JunctionOneError):
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


class TimeOutError(RequestError):
    """Raised when a request times out."""


class AsyncTimeOutError(JunctionOneError):
    """Raised when the async function exceeds the timeout duration."""
