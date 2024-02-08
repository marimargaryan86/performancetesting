import base64
import hashlib
import hmac

from starlette import exceptions, requests, status


def generate_signature(secret: bytes, payload: bytes, timestamp: str) -> str:
    signed_payload = timestamp.encode() + b"." + payload  # noqa: WPS336
    signature = hmac.new(secret, signed_payload, hashlib.sha256).digest()
    return base64.b16encode(signature).lower().decode()


class WebhookSignatureValidator(object):
    def __init__(self, secret: str):
        self.secret = secret.encode("utf-8")

    async def authenticate(self, request: requests.Request) -> bool:
        if not (await self._validate_signature(request)):
            raise exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return True

    # from https://duffel.com/docs/guides/receiving-webhooks
    # rewritten to support starlette requests
    async def _validate_signature(self, request: requests.Request) -> bool:
        raw_payload = await request.body()
        raw_signature = request.headers["X-Duffel-Signature"]
        pairs = [x.split("=") for x in raw_signature.split(",")]  # noqa: WPS111
        t = pairs[0][1]  # noqa: WPS111
        v1 = pairs[1][1]  # noqa: WPS111

        local_signature = generate_signature(self.secret, raw_payload, t)

        return hmac.compare_digest(v1, local_signature)
