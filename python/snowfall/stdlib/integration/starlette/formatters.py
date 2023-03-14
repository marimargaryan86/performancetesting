import datetime
import functools
from typing import Any

import email_validator
import iso4217
import isodate
import phonenumbers
import pycountry
import rfc3339_validator
from furl import furl
from openapi_core.unmarshalling.schemas import datatypes as unmarshalling_datatypes
from openapi_core.validation.schemas import datatypes as validation_datatypes


def _validate_format_factory(
    formatter: unmarshalling_datatypes.FormatUnmarshaller,
) -> validation_datatypes.FormatValidator:
    def wrapper(maybe_correct: Any) -> bool:
        try:
            formatter(maybe_correct)
        except (TypeError, ValueError):
            return False

        return True

    return wrapper


def _unmarshal_country(country_code: Any) -> pycountry.db.Data:
    if not isinstance(country_code, str):
        raise TypeError

    country = pycountry.countries.get(alpha_2=country_code)

    if not country:
        raise ValueError

    return country


def _unmarshal_currency(currency_code: Any) -> iso4217.Currency:
    if not isinstance(currency_code, str):
        raise TypeError

    return iso4217.Currency(currency_code)


def _unmarshal_date_time(date_time: Any) -> datetime.datetime:
    if not isinstance(date_time, str):
        raise TypeError

    if not rfc3339_validator.validate_rfc3339(date_time):
        raise ValueError

    try:
        return isodate.parse_datetime(date_time)
    except isodate.ISO8601Error as err:
        raise ValueError from err


def _unmarshal_email(email: Any) -> str:
    if not isinstance(email, str):
        raise TypeError

    try:
        return email_validator.validate_email(
            email=email,
            check_deliverability=False,
        ).email
    except email_validator.EmailNotValidError as err:
        raise ValueError from err


def _unmarshal_phone(phone_number: Any) -> phonenumbers.PhoneNumber:
    if not isinstance(phone_number, str):
        raise TypeError

    try:
        phone = phonenumbers.parse(phone_number, None)
    except phonenumbers.NumberParseException as err:
        raise ValueError from err

    if not phonenumbers.is_valid_number(phone):
        raise ValueError

    return phone


def _unmarshal_uri(uri: Any) -> furl:
    if not isinstance(uri, str):
        raise TypeError

    uri_obj = furl(uri)

    if not uri_obj.scheme:
        raise ValueError

    return uri_obj


@functools.cache
def format_unmarshallers() -> unmarshalling_datatypes.FormatUnmarshallersDict:
    return {
        "country": _unmarshal_country,
        "currency": _unmarshal_currency,
        "date-time": _unmarshal_date_time,
        "email": _unmarshal_email,
        "phone": _unmarshal_phone,
        "uri": _unmarshal_uri,
    }


@functools.cache
def format_validators() -> validation_datatypes.FormatValidatorsDict:
    return {
        "country": _validate_format_factory(_unmarshal_country),
        "currency": _validate_format_factory(_unmarshal_currency),
        "date-time": _validate_format_factory(_unmarshal_date_time),
        "email": _validate_format_factory(_unmarshal_email),
        "phone": _validate_format_factory(_unmarshal_phone),
        "uri": _validate_format_factory(_unmarshal_uri),
    }
