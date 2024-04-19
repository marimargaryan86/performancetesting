class SilverrailBaseError(Exception):
    """Base for all Silverrail errors."""


class SilverrailUnexpectedFormatError(SilverrailBaseError):
    """Raised when the message retunred by Silverrail had an unexpected format."""


class RequestFailedError(Exception):
    """Raised when the request didn't succeed."""
