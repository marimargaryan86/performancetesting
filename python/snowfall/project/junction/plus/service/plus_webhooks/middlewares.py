import hashlib
import hmac
from collections.abc import Awaitable, Callable

from starlette import applications, exceptions, requests, responses, status
from starlette.middleware.base import BaseHTTPMiddleware
from twilio.request_validator import RequestValidator

from snowfall.stdlib.integration.starlette import handlers


def calculate_hash(
    received_key: bytes,
    secret_key: bytes,
) -> str:
    hmac_obj = hmac.new(
        secret_key,
        received_key,
        hashlib.sha512,
    )
    return hmac_obj.hexdigest()


def validate_hmac(
    received_key: bytes,
    received_hash: bytes,
    secret_key: bytes,
) -> bool:
    calculated_hash = calculate_hash(received_key, secret_key)
    return hmac.compare_digest(received_hash, calculated_hash.encode())


class HmacHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        secret_key: str,
        twilio_validator: RequestValidator,
    ):
        super().__init__(app)
        self._secret_key = secret_key
        self._twilio_validator = twilio_validator

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        if request.scope["path"].endswith("alerts"):
            try:
                return await call_next(
                    await self.flight_stats_dispatch(request),
                )
            except exceptions.HTTPException as flight_stats_exc:
                return handlers.error_response_from_status(flight_stats_exc.status_code)

        if request.scope["path"].endswith("whatsapp"):
            try:
                return await call_next(
                    await self.whatsapp_dispatch(request),
                )
            except exceptions.HTTPException as whatsapp_exc:
                return handlers.error_response_from_status(whatsapp_exc.status_code)

        return await call_next(request)

    async def flight_stats_dispatch(
        self,
        request: requests.Request,
    ) -> requests.Request:
        received_hash = request.headers.get("Cirium-Flex-Alert-Hash")
        received_key = request.headers.get("Cirium-Flex-Alert-Key")
        if received_key is None or received_hash is None:
            raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        is_valid_hmac = validate_hmac(
            received_key.encode(),
            received_hash.encode(),
            self._secret_key.encode(),
        )
        if not is_valid_hmac:
            raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return request

    async def whatsapp_dispatch(
        self,
        request: requests.Request,
    ) -> requests.Request:
        await request.body()  # needed in order for Starlette to cache the body stream
        is_valid = self._twilio_validator.validate(  # type: ignore[no-untyped-call]
            str(request.url),
            await request.form(),
            request.headers.get("x-twilio-signature"),
        )
        if not is_valid:
            raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return request
