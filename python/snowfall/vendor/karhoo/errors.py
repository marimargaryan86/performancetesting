class KarhooError(Exception):
    """Raised when there is a Karhoo-related issue."""


class ServiceError(KarhooError):
    """Raised when the Karhoo service is unhealthy."""
