class PaymentError(Exception):
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
