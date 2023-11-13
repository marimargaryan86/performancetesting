import datetime


def date_to_age(
    date_of_birth: datetime.date,
    at_date: datetime.date | None = None,
) -> int:
    if not at_date:
        at_date = datetime.datetime.now(tz=datetime.UTC).date()

    return (
        at_date.year
        - date_of_birth.year
        - ((at_date.month, at_date.day) < (date_of_birth.month, date_of_birth.day))
    )
