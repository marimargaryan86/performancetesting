class AccountForgottenPasswordTokenAlreadyUsedError(Exception):
    """Raised when an AccountForgottenPassword Token has already been used."""


class AccountForgottenPasswordTokenExpiredError(Exception):
    """Raised when an AccountForgottenPassword Token has expired."""


class AccountForgottenPasswordNotFoundError(Exception):
    """Raised when an AccountForgottenPassword cannot be found."""


class AccountNotFoundError(Exception):
    """Raised when an Account cannot be found."""


class AccountEmailAlreadyUsedError(Exception):
    """Raised when an Account Email has already been used."""


class KnownAccountNotFoundError(Exception):
    """Raised when known/existing Account cannot be found."""
