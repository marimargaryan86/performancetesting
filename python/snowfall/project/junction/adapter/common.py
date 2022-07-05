import dataclasses
from typing import Generic, Sequence, TypeVar

from google.protobuf import message

Proto = TypeVar("Proto", bound=message.Message)


@dataclasses.dataclass(frozen=True)
class ItemsPage(Generic[Proto]):
    protos: Sequence[Proto]
    next_page_token: str = ""
