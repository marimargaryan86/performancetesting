class SATError(Exception):
    """SAT client base exception."""


class SATValidationError(SATError):
    """SAT client validation exception."""


class SATValueError(SATError):
    """SAT client value error."""
