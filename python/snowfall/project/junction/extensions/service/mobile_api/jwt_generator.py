import dataclasses
from typing import Any

from snowfall.stdlib.format import jwt


@dataclasses.dataclass(kw_only=True, frozen=True)
class _ClientPayload(jwt.Payload):
    client_id: str
    version: str


class JwtGenerator:
    def __init__(self, encoder: jwt.Encoder, token_version: str):
        self._encoder = encoder
        self._token_version = token_version

    def encode(self, client_id: str) -> Any:
        return self._encoder.encode(
            _ClientPayload(client_id=client_id, version=self._token_version),
        )
