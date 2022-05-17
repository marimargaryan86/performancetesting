from datetime import date


def date_to_age(date_of_birth: date) -> int:
    today = date.today()
    return (
        today.year
        - date_of_birth.year
        - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    )
