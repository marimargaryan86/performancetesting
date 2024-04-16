import http
from collections.abc import Awaitable, Callable, Container

import sentry_sdk
from openapi_core import protocols
from starlette import (
    applications,
    requests,
    responses,
)
from starlette.middleware import base

from snowfall.stdlib.integration.starlette import handlers, validation
from snowfall.stdlib.logging import stdout


class RequestIdMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        response = await call_next(request)
        transaction = sentry_sdk.Hub.current.scope.transaction

        if transaction:
            response.headers["X-Request-Id"] = transaction.trace_id

        return response


class SecurityHeadersMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        response = await call_next(request)
        response.headers.update(
            {
                "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            },
        )

        return response


class ValidationMiddleware(base.BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        validator: validation.Validator,
        *,
        excluded_status_codes: Container[int] | None = None,
        validate_responses: bool = True,
    ):
        super().__init__(app)
        self._logger = stdout.get_logger()
        self._response_logger = stdout.get_logger()
        self._validator = validator
        self._excluded_status_codes = excluded_status_codes or []
        self._validate_responses = validate_responses

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        openapi_request = await self._validator.get_openapi_request(request)
        openapi_result = await self._validator.validate_request(openapi_request)
        errors = list(validation.openapi_errors_to_errors(openapi_result.errors))

        if errors:
            return await handlers.multiple4xx_error_handler(
                request=request,
                errors=errors,
            )

        request.scope["parsed_query_string"] = openapi_result.parameters.query
        request.scope["security"] = openapi_result.security

        return await self._dispatch(call_next, request, openapi_request)

    async def _dispatch(
        self,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
        request: requests.Request,
        openapi_request: protocols.Request,
    ) -> responses.Response:
        response = await call_next(request)

        if response.status_code in self._excluded_status_codes:
            return response

        if self._validate_responses:
            return await self._validate_response(
                openapi_request=openapi_request,
                response=response,
            )

        return response

    async def _validate_response(
        self,
        openapi_request: protocols.Request,
        response: responses.Response,
    ) -> responses.Response:
        openapi_response = await self._validator.get_openapi_response(response)
        openapi_result = await self._validator.validate_response(
            openapi_request,
            openapi_response,
        )
        errors = list(validation.openapi_errors_to_errors(openapi_result.errors))

        if errors:
            self._response_logger.error(
                "Response body does not validate against schema",
                body=openapi_response.data.decode() if openapi_response.data else None,
                errors=[error.model_dump() for error in errors],
            )

            return handlers.error_response_from_status(
                int(http.HTTPStatus.INTERNAL_SERVER_ERROR),
            )

        return response
