class DuffelError(Exception):
    """Raised when there is an Duffel-related issue."""


class ServiceError(DuffelError):
    """Raised when the Duffel service is unhealthy."""
