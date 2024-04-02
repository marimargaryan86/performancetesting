from collections.abc import Awaitable, Callable

from starlette import applications
from starlette.middleware import base
from starlette.requests import Request
from starlette.responses import Response

from snowfall.vendor.junction_one.auth import TemporaryTokenAuth


class JunctionOneClientMiddleware(base.BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        *,
        token_auth: TemporaryTokenAuth,
    ):
        super().__init__(app)
        self._token_auth = token_auth

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not request.user.is_authenticated:
            return await call_next(request)
        with self._token_auth.temporary(request.user.username):
            return await call_next(request)
