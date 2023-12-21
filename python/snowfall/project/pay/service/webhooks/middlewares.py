import hashlib
import hmac
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

import stripe
from starlette import applications, exceptions, requests, responses, status
from starlette.middleware.base import BaseHTTPMiddleware

from snowfall.stdlib.integration.starlette.middlewares import resolve_request


def validate_hmac(
    message: bytes,
    secret_key: bytes,
    received_hmac: bytes,
) -> bool:
    hmac_obj = hmac.new(
        secret_key,
        message,
        hashlib.sha512,
    )
    calculated_hmac = hmac_obj.hexdigest()
    return hmac.compare_digest(received_hmac, calculated_hmac.encode())


class HmacHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        secret_key: str,
        stripe_secret_key: str,
    ):
        super().__init__(app)
        self._secret_key = secret_key
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
        is_currency_cloud = self.verify_currency_cloud(payload, request.headers)
        is_stripe = (
            False if is_currency_cloud else self.verify_stripe(payload, request.headers)
        )
        if not is_currency_cloud and not is_stripe:
            raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return await call_next(resolved_request)

    def verify_currency_cloud(
        self,
        payload: bytes,
        headers: Mapping[str, Any],
    ) -> bool:
        received_hmac = headers.get("X-Hmac-Digest-Sha-512")
        if not received_hmac:
            return False
        return validate_hmac(
            payload,
            self._secret_key.encode(),
            received_hmac.encode(),
        )

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
