from datetime import date, datetime


def convert_datetime_to_date(datetime_value: datetime) -> date:
    return datetime.fromisoformat(str(datetime_value)).date()
