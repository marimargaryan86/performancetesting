from typing import Awaitable, Callable

from starlette import applications, requests, responses, status
from starlette.middleware import base

from snowfall.junction.client_api import validation


class ValidationMiddleware(base.BaseHTTPMiddleware):
    def __init__(self, app: applications.Starlette, validator: validation.Validator):
        super().__init__(app)
        self._validator = validator

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        response = await call_next(request)

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return response

        return await self._validator.validate(request, response)
