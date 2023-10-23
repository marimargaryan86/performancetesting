import base64
import hashlib
import hmac

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class ZendeskSignatureValidator(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, secret: str):
        super().__init__(app)
        self._secret = secret

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        signature_is_valid = await self._validate(
            request.headers.get("x-zendesk-webhook-signature", ""),
            request.headers.get("x-zendesk-webhook-signature-timestamp", ""),
            await request.body(),
        )
        if signature_is_valid:
            return await call_next(request)
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=None)

    async def _validate(self, signature: str, timestamp: str, payload: bytes) -> bool:
        signed_payload = timestamp.encode() + payload
        calculated_signature = hmac.new(
            self._secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).digest()
        calculated_signature = base64.b64encode(calculated_signature)

        return hmac.compare_digest(signature.encode(), calculated_signature)
