from base64 import b64decode
from datetime import datetime, timedelta
from typing import Mapping

import jwt
from cryptography.hazmat.primitives import serialization


class JWTEncoder(object):
    """Encoding JWT using RS256 algorithm."""

    def __init__(
        self,
        jwt_token_version: str,
        private_key_content: str = "",
        token_expiration: int = 3600,
        algorithm: str = "RS256",
    ):
        self._jwt_token_version = jwt_token_version
        self._private_key_content = private_key_content
        self._token_expiration = token_expiration
        self._algorithm = algorithm

    def encode(
        self,
        payload: Mapping[str, str],
    ) -> str:
        """Generate JWT token."""
        jwt_info = {
            "user_info": payload,
            "client_id": "client_id",  # TODO: make me dynamic or move to metadata obj
            "exp": datetime.utcnow() + timedelta(seconds=self._token_expiration),
            "version": self._jwt_token_version,
        }

        b64_private_key = b64decode(self._private_key_content.encode()).decode()
        key = serialization.load_pem_private_key(
            data=b64_private_key.encode(),
            password=None,
        )

        return jwt.encode(
            jwt_info,
            key,  # type: ignore[arg-type]
            algorithm=self._algorithm,
        )


class JWTDecoder(object):
    """Decoding JWT using RS256 algorithm."""

    def __init__(self, public_key_content: str, algorithm: str):
        self._public_key_content = public_key_content
        self._algorithm = algorithm

    def get_user_payload(
        self,
        jwt_token: str,
    ) -> Mapping[str, str]:
        return self.decode(jwt_token)["user_info"]

    def decode(
        self,
        jwt_token: str,
    ) -> Mapping[str, Mapping[str, str]]:
        return jwt.decode(
            jwt_token,
            self._public_key_content,
            algorithms=[self._algorithm],
        )
