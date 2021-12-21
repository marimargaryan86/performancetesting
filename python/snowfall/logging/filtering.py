import re
from typing import Any, MutableMapping

FILTERED_WORD = "[Filtered]"
SECRET_WORDS = (
    "password",
    "passwd",
    "pwd",
    "secret",
    "api_key",
    "apikey",
    "credentials",
    "access_token",
)
_RE_SECRET_WORDS = re.compile("|".join(SECRET_WORDS), re.IGNORECASE)


def filter_secrets_dict(
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    for key, item_value in event_dict.items():
        if is_key_secret(key):
            event_dict[key] = FILTERED_WORD
        else:
            event_dict[key] = filter_secrets_value(item_value)

    return event_dict


def filter_secrets_list(event_list: list[Any]) -> list[Any]:
    for idx, item_value in enumerate(event_list):
        event_list[idx] = filter_secrets_value(item_value)

    return event_list


def filter_secrets_value(item_value: Any) -> Any:
    if isinstance(item_value, dict):
        return filter_secrets_dict(item_value)
    elif isinstance(item_value, list):
        return filter_secrets_list(item_value)

    return item_value


def is_key_secret(key: str) -> bool:
    return _RE_SECRET_WORDS.search(str(key)) is not None
