import dataclasses
import datetime
from typing import Mapping

from snowfall.service.authentication.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import jwt


@dataclasses.dataclass(frozen=True)
class _UserInfo(object):
    id: str  # noqa: A003
    email: str
    metadata: Mapping[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(kw_only=True, frozen=True)
class Version2Payload(jwt.Payload):
    user_info: _UserInfo
    version: str = dataclasses.field(default="2.0.0", init=False)


class JWTFactory(object):
    def __init__(
        self,
        ttl: datetime.timedelta,
    ):
        self._ttl = ttl

    def from_user(self, user: models_pb2.User) -> Version2Payload:
        return Version2Payload(
            user_info=_UserInfo(
                id=user.id,
                email=user.email,
                metadata=dict(user.metadata),
            ),
            exp=datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
            jti=string.uuid(),
        )
