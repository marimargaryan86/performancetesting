class Ask2GoError(Exception):
    """Raised when an Ask2Go is unhealthy."""


class ServiceError(Ask2GoError):
    def __init__(self) -> None:
        super().__init__("Service unavailable")


class DateError(Ask2GoError):
    """Raised when Inbound date is lower than outbound date."""
