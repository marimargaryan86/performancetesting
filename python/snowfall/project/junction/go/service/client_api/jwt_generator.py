from base64 import b64decode
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization
from pydantic import BaseSettings


class Settings(BaseSettings):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.jwt_private_key = b64decode(self.jwt_private_key.encode()).decode()

    jwt_token_version: str
    jwt_private_key: str


settings = Settings()
payload = {"version": settings.jwt_token_version, "client_id": "velocity-black"}

key = serialization.load_pem_private_key(
    data=settings.jwt_private_key.encode(),
    password=None,
)

token = jwt.encode(payload=payload, key=key, algorithm="RS256")  # type: ignore[arg-type]
print(token)  # noqa: T201, WPS421
