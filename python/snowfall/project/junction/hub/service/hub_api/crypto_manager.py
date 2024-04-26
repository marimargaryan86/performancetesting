import base64
import datetime
import hashlib
import json
from collections.abc import Mapping

from cryptography.fernet import Fernet, InvalidToken


class CryptoManagerError(Exception):
    """Raised when the token is not valid."""


class CryptoManager:
    def __init__(self, key: bytes, ttl: datetime.timedelta) -> None:
        self._ttl = ttl
        self._cipher = Fernet(base64.urlsafe_b64encode(hashlib.sha256(key).digest()))

    def encrypt(self, payload: Mapping[str, str]) -> str:
        json_data = json.dumps(
            {
                **payload,
                "exp": (datetime.datetime.now(tz=datetime.UTC) + self._ttl).timestamp(),
            },
        )

        return self._cipher.encrypt(json_data.encode()).decode()

    def decrypt(self, encrypted_message: str) -> Mapping[str, str]:
        try:
            decrypted_data = self._cipher.decrypt(encrypted_message.encode()).decode()
        except InvalidToken as err:
            raise CryptoManagerError("Invalid token.") from err

        payload = json.loads(decrypted_data)

        if float(payload["exp"]) < datetime.datetime.now(tz=datetime.UTC).timestamp():
            raise CryptoManagerError("Token is expired.")

        return payload
