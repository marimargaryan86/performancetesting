import json
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

import stripe
from starlette import applications, exceptions, requests, responses, status
from starlette.middleware.base import BaseHTTPMiddleware

from snowfall.stdlib.integration.starlette.middlewares import resolve_request


class SignatureVerificationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        stripe_secret_key_for_refund: str,
        stripe_secret_key_for_invoice: str,
    ):
        super().__init__(app)
        self._stripe_secret_key_for_refund = stripe_secret_key_for_refund
        self._stripe_secret_key_for_invoice = stripe_secret_key_for_invoice

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        if request.scope["path"].endswith("health"):
            return await call_next(request)
        resolved_request = await resolve_request(request)
        body = await resolved_request.body()

        payload = json.loads(body)
        is_authenticated = False

        if payload["data"]["object"]["object"] == "invoice":
            is_authenticated = self.verify_stripe(
                body,
                request.headers,
                self._stripe_secret_key_for_invoice,
            )
        elif payload["data"]["object"]["object"] == "charge":
            is_authenticated = self.verify_stripe(
                body,
                request.headers,
                self._stripe_secret_key_for_refund,
            )

        if not is_authenticated:
            raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return await call_next(resolved_request)

    def verify_stripe(
        self,
        body: bytes,
        headers: Mapping[str, Any],
        secret_key: str,
    ) -> bool:
        try:
            stripe.Webhook.construct_event(  # type: ignore[no-untyped-call]
                body,
                headers.get("stripe-signature", ""),
                secret_key,
            )
        except stripe.SignatureVerificationError:
            return False
        return True
