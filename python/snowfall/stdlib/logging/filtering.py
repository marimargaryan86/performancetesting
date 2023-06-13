import re
from typing import Any, Mapping, Sequence

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
    event_dict: Mapping[str, Any],
) -> dict[str, Any]:
    filtered_events = {}

    for key, item_value in event_dict.items():
        if is_key_secret(key):
            filtered_events[key] = FILTERED_WORD
        else:
            filtered_events[key] = filter_secrets_value(item_value)

    return filtered_events


def filter_secrets_list(event_list: Sequence[Any]) -> list[Any]:
    return [filter_secrets_value(event_value) for event_value in event_list]


def filter_secrets_value(item_value: Any) -> Any:
    if isinstance(item_value, dict):
        return filter_secrets_dict(item_value)
    if isinstance(item_value, list):
        return filter_secrets_list(item_value)

    return item_value


def is_key_secret(key: str) -> bool:
    return _RE_SECRET_WORDS.search(str(key)) is not None
