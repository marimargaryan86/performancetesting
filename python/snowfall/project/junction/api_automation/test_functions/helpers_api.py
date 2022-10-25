import json
import logging
from functools import wraps
from typing import Any, Callable
from uuid import UUID


def is_valid_uuid(
    uuid_to_test: str,
    version: int = 4,
) -> Any:
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


def with_log(function: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Add some logging to any async function."""

    @wraps(function)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Call the original function and then write to the log."""
        res = await function(*args, **kwargs)
        logging.info("%s: %s", function.__name__, json.dumps(res, indent=4))
        return res

    return wrapper
