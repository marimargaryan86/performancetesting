import datetime


def date_to_age(date_of_birth: datetime.date) -> int:
    today = datetime.datetime.now(tz=datetime.UTC)

    return (
        today.year
        - date_of_birth.year
        - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    )
