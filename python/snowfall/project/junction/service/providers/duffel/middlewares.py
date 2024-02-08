from collections.abc import Awaitable, Callable

from starlette import applications, requests, responses
from starlette.middleware.base import BaseHTTPMiddleware

from snowfall.project.junction.service.providers.duffel import (
    signature_validator,
)
from snowfall.stdlib.integration.starlette.middlewares import resolve_request


class SignatureValidationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        validator: signature_validator.WebhookSignatureValidator,
    ):
        super().__init__(app)
        self._validator = validator

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        resolved_request = await resolve_request(request)
        await self._validator.authenticate(resolved_request)
        return await call_next(resolved_request)
