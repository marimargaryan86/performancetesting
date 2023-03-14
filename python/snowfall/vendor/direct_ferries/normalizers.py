import datetime
from urllib import parse as parse_url


def datetime_str_to_date(datetime_str: str | datetime.date) -> datetime.date | None:
    if not datetime_str:
        return None

    if isinstance(datetime_str, str):
        return datetime.date.fromisoformat(datetime_str[:10])

    return datetime_str


def normalize_booking_token(token: str) -> str:
    return parse_url.unquote(token)
