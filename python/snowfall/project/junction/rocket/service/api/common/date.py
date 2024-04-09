from datetime import date, datetime


def convert_datetime_to_date(datetime_value: str) -> date:
    return datetime.fromisoformat(datetime_value).date()
