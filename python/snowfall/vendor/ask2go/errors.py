class Ask2GoError(Exception):
    """Raised when there is an Ask2Go-related issue."""


class ServiceError(Ask2GoError):
    """Raised when the Ask2Go service is unhealthy."""


class DateError(Ask2GoError):
    """Raised when Inbound date is lower than outbound date."""


class TimeOutError(Ask2GoError):
    """Raised when a request times out."""
