class DistribusionError(Exception):
    """Raised when there is an Distribusion-related issue."""


class ServiceError(DistribusionError):
    """Raised when the Distribusion service is unhealthy."""
