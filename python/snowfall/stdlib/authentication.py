import dataclasses
from typing import Any


class AuthenticationError(Exception):
    """Raised when a user is not authenticated."""


@dataclasses.dataclass(frozen=True)
class User(object):
    identifier: str
    email: str
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)
