from abc import ABC, abstractmethod
from typing import Generic, Tuple, TypeVar

TO_VALIDATE = TypeVar("TO_VALIDATE")


class Validator(ABC, Generic[TO_VALIDATE]):
    @abstractmethod
    async def is_valid(self, to_validate: TO_VALIDATE) -> Tuple[bool, list[str]]:
        raise NotImplementedError()
