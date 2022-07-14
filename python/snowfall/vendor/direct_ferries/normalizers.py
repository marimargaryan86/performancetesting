import datetime
from typing import Union


def datetime_str_to_date(datetime_str: Union[str, datetime.date]) -> datetime.date:
    if isinstance(datetime_str, str):
        return datetime.date.fromisoformat(datetime_str[:10])

    return datetime_str
