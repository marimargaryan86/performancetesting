import hashlib
import hmac
from typing import Awaitable, Callable

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
    def __init__(self, app: applications.Starlette, secret_key: str):
        super().__init__(app)
        self._secret_key = secret_key

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        resolved_request = await resolve_request(request)
        received_hmac = request.headers.get("X-Hmac-Digest-Sha-512")
        if not received_hmac:
            raise exceptions.HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="hmac value is missing",
            )
        json_data = await resolved_request.body()
        is_valid_hmac = validate_hmac(
            json_data,
            self._secret_key.encode(),
            received_hmac.encode(),
        )
        if not is_valid_hmac:
            raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return await call_next(resolved_request)
