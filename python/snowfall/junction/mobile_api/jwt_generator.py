from base64 import b64decode
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization


class JwtGenerator(object):
    def __init__(self, jwt_private_key: str, jwt_token_version: str):
        self.jwt_private_key = b64decode(jwt_private_key.encode()).decode()
        self.key = serialization.load_pem_private_key(
            data=self.jwt_private_key.encode(),
            password=None,
        )
        self.jwt_token_version = jwt_token_version

    def encode(self, client_id: str) -> Any:
        return jwt.encode(
            payload={
                "client_id": client_id,
                "version": self.jwt_token_version,
            },
            key=self.key,  # type: ignore[arg-type]
            algorithm="RS256",
        )
