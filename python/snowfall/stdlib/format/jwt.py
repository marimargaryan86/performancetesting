import base64
import dataclasses
import datetime
from typing import Any, Mapping, Sequence

import jwt

from snowfall.stdlib import types


@dataclasses.dataclass(frozen=True)
class Payload(object):
    custom: Mapping[str, types.Primitive] = dataclasses.field(default_factory=dict)
    iss: str | None = None
    sub: str | None = None
    aud: str | None = None
    exp: int | datetime.datetime | None = None
    nbf: int | datetime.datetime | None = None
    iat: int | datetime.datetime | None = None
    jti: str | None = None


class Encoder(object):
    def __init__(
        self,
        private_key: str | None = None,
        algorithm: str = "HS256",
    ):
        self._algorithm = algorithm
        self._key = ""

        if private_key:
            self._key = _decode_base64_key(private_key)

        # Verify that the chosen algorithm works with the provided key.
        jwt.encode({}, self._key, algorithm=self._algorithm)

    def encode(self, payload: Payload) -> str:
        return jwt.encode(
            {
                jwt_key: jwt_value
                for jwt_key, jwt_value in dataclasses.asdict(payload).items()
                if jwt_value is not None
            },
            self._key,
            algorithm=self._algorithm,
        )


class Decoder(object):
    def __init__(
        self,
        public_key: str | None = None,
        algorithms: Sequence[str] | None = None,
    ):
        self._algorithms = ["HS256"]
        self._key = ""

        if public_key:
            self._key = _decode_base64_key(public_key)

        if algorithms:
            self._algorithms = list(algorithms)

    def decode(
        self,
        jwt_token: str,
    ) -> Mapping[str, Any]:
        return jwt.decode(
            jwt_token,
            self._key,
            algorithms=self._algorithms,
        )


def _decode_base64_key(encoded_key: str) -> str:
    return base64.b64decode(encoded_key.encode()).decode()
