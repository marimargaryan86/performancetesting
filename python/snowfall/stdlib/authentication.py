import dataclasses


class AuthenticationError(Exception):
    """Raised when a user is not authenticated."""


@dataclasses.dataclass(frozen=True)
class User:
    identifier: str
    email: str
    metadata: dict[str, object] = dataclasses.field(default_factory=dict)
