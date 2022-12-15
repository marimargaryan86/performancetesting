from __future__ import annotations

import dataclasses
import http
import inspect
import json
from typing import Any

import httpx


@dataclasses.dataclass(frozen=True)
class RequestMetaData(object):
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
class ResponseMetaData(object):
    status_code: int
    body: str | None

    @classmethod
    def from_error(cls, error: httpx.HTTPStatusError) -> ResponseMetaData:
        return cls(
            status_code=error.response.status_code,
            body=error.response.content.decode() or None,
        )


class HttpError(Exception):
    """Raised when there is HTTP client-related issue."""


class RequestError(HttpError):
    """Raised when a request fails."""

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


class HttpStatusError(HttpError):
    """Raised when a response is not 2XX."""

    def __init__(
        self,
        body: Any,
        status: http.HTTPStatus,
        request: RequestMetaData,
        response: ResponseMetaData,
    ):
        super().__init__(status.description)
        self.body = body
        self.status = status
        self.request = request
        self.response = response

    @classmethod
    def from_error(cls, error: httpx.HTTPStatusError) -> HttpStatusError:
        try:
            body = error.response.json()
        except json.decoder.JSONDecodeError:
            body = error.response.content.decode()

        return cls(
            body=body,
            status=http.HTTPStatus(error.response.status_code),
            request=RequestMetaData.from_error(error),
            response=ResponseMetaData.from_error(error),
        )


class TimeOutError(RequestError):
    """Raised when a request times out."""
