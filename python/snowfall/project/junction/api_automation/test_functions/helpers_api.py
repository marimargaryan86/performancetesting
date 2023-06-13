import json
import logging
import secrets
import string
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec
from uuid import UUID


def is_valid_uuid(
    uuid_to_test: str,
    version: int = 4,
) -> bool:
    """Check if uuid_to_test is a valid UUID.

    param: uuid_to_test : str
    param: version : {1, 2, 3, 4}

    return: `True` if uuid_to_test is a valid UUID, otherwise `False`.

    Examples:
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


P = ParamSpec("P")  # noqa: WPS111


def with_log(function: Callable[P, Any]) -> Callable[P, Any]:
    """Add some logging to any async function."""

    @wraps(function)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        """Call the original function and then write to the log."""
        res = await function(*args, **kwargs)
        logging.info("%s: %s", function.__name__, json.dumps(res, indent=4))
        return res

    return wrapper


def return_randomized_token() -> str:
    alphabet = string.ascii_letters + string.digits
    length_of_string = 32
    return "".join(secrets.choice(alphabet) for ii in range(length_of_string))
