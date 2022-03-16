import datetime
import zoneinfo
from typing import Any, Callable, Optional, Sequence, Union

import phonenumbers
import pycountry
from pydantic import typing, validator

from snowfall.stdlib.format.gtfs import constants


def normalize_currency(currency: Optional[str]) -> Optional[str]:
    if currency is None:
        return None

    currency_obj = pycountry.currencies.get(alpha_3=currency)

    if not currency_obj:
        raise ValueError("{value} is not a valid currency".format(value=currency))

    return currency


def normalize_date(date: Optional[str]) -> Optional[datetime.date]:
    if date is None:
        return None

    try:
        return datetime.datetime.strptime(date, "%Y%m%d").date()
    except ValueError:
        # A JSON-serialized model will contain ISO.
        return datetime.date.fromisoformat(date)


def normalize_language_code(code: Optional[str]) -> Optional[str]:
    if code is None:
        return None

    if not constants.LANGUAGE_REGEX.fullmatch(code):
        raise ValueError("{value} is not a valid language code".format(value=code))

    parts = code.split("-")

    language = pycountry.languages.get(alpha_2=parts[0])

    if not language:
        raise ValueError("{value} is not a valid language code".format(value=code))

    if len(parts) == 2:
        country = pycountry.countries.get(alpha_2=parts[1])

        if not country:
            raise ValueError("{value} is not a valid language code".format(value=code))

    return code


def normalize_phone_number(phone: Optional[str]) -> Optional[str]:
    if phone is None:
        return None

    try:
        parsed = phonenumbers.parse(phone)
    except phonenumbers.NumberParseException:
        return None

    return phonenumbers.format_number(
        parsed,
        phonenumbers.PhoneNumberFormat.E164,
    )


def normalize_time(
    time: Optional[Union[float, str]],
) -> Optional[Union[float, datetime.timedelta]]:
    if time is None:
        return None

    # A JSON-serialized model will contain float.
    if isinstance(time, float):
        return datetime.timedelta(seconds=time)

    parts = [int(segment) for segment in time.split(":")]

    if len(parts) != 3:
        raise ValueError("{value} is not a valid time".format(value=time))

    return datetime.timedelta(
        hours=parts[0],
        minutes=parts[1],
        seconds=parts[2],
    )


def normalize_time_zone(tz: Optional[str]) -> Optional[str]:
    if tz is None:
        return None

    try:
        zoneinfo.ZoneInfo(tz)
    except (ValueError, zoneinfo.ZoneInfoNotFoundError) as err:
        raise ValueError("{value} is not a valid time zone".format(value=tz)) from err

    return tz


def normalizer(
    properties: Sequence[str],
    func: Callable[[Optional[str]], Any],
) -> "typing.AnyClassMethod":
    return validator(*properties, pre=True, allow_reuse=True)(func)
