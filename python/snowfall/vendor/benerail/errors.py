class BenerailError(Exception):
    """Raised when there is a Benerail-related issue."""


class ServiceError(BenerailError):
    """Raised when the Benerail service is unhealthy."""
