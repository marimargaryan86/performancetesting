class CurrencyCloudError(Exception):
    """Payment client specific exception."""

    def __init__(
        self,
        message: str,
        status: int = 400,
        code: str = "bad_request",
    ):
        super().__init__()
        self.message = message
        self.status = status
        self.code = code

    def __repr__(self) -> str:
        return "<{0}({1}), {2}>".format(
            self.__class__.__name__,
            self.message,
            self.status,
        )
