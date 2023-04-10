from typing import Sequence


class CurrencyCloudError(Exception):
    """Payment client specific exception."""

    def __init__(
        self,
        messages: Sequence[str],
        status: int = 400,
        code: str = "bad_request",
    ):
        super().__init__()
        self.messages = messages
        self.status = status
        self.code = code

    def __str__(self) -> str:
        return "<{0}({1}), {2}>".format(
            self.__class__.__name__,
            ", ".join(self.messages),
            self.status,
        )
