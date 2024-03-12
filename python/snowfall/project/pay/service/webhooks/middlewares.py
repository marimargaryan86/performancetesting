from collections.abc import Awaitable, Callable, Mapping
from typing import Any

import stripe
from starlette import applications, exceptions, requests, responses, status
from starlette.middleware.base import BaseHTTPMiddleware

from snowfall.stdlib.integration.starlette.middlewares import resolve_request


class HmacHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        stripe_secret_key: str,
    ):
        super().__init__(app)
        self._stripe_secret_key = stripe_secret_key

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        if request.scope["path"].endswith("health"):
            return await call_next(request)
        resolved_request = await resolve_request(request)
        payload = await resolved_request.body()

        is_stripe = self.verify_stripe(payload, request.headers)

        if is_stripe:
            raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return await call_next(resolved_request)

    def verify_stripe(
        self,
        payload: bytes,
        headers: Mapping[str, Any],
    ) -> bool:
        try:
            stripe.Webhook.construct_event(  # type: ignore[no-untyped-call]
                payload,
                headers.get("stripe-signature", ""),
                self._stripe_secret_key,
            )
        except stripe.SignatureVerificationError:
            return False
        return True
