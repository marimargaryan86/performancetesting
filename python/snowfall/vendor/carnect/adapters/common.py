from abc import ABC, abstractmethod

from snowfall.vendor.carnect.models.service import (
    ArrayOfErrorType,
    ArrayOfWarningType,
    ErrorType,
    WarningType,
)


def get_error_text(errors: ArrayOfErrorType | None) -> str | None:
    if errors and errors.error:
        return "\n".join([_get_error(error) for error in errors.error])

    return None


def get_warning_text(warnings: ArrayOfWarningType | None) -> str | None:
    if warnings and warnings.warning:
        return "\n".join([_get_warning(warning) for warning in warnings.warning])

    return None


def _get_error(error: ErrorType) -> str:
    return "{code}: {value}".format(code=error.code, value=error.value)


def _get_warning(warning: WarningType) -> str:
    return "{code}: {value}".format(code=warning.code, value=warning.value)


class BaseAdapter(ABC):
    @abstractmethod
    def is_success(self) -> bool:
        """Return True when response is successful."""

    @abstractmethod
    def get_error(self) -> str | None:
        """Return error text."""

    @abstractmethod
    def get_warning(self) -> str | None:
        """Return warning text."""
