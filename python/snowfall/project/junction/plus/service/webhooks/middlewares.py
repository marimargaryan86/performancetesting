import hashlib
import hmac
from collections.abc import Awaitable, Callable

from starlette import applications, exceptions, requests, responses, status
from starlette.middleware.base import BaseHTTPMiddleware

from snowfall.stdlib.integration.starlette.middlewares import resolve_request


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
    def __init__(self, app: applications.Starlette, secret_key: str):
        super().__init__(app)
        self._secret_key = secret_key

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        if request.scope["path"].endswith("health"):
            return await call_next(request)
        resolved_request = await resolve_request(request)
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

        return await call_next(resolved_request)
