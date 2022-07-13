import uuid
from typing import Protocol

import pytest
from jsonschema import exceptions
from openapi_core.unmarshalling.schemas import util

from snowfall.stdlib.integration.starlette import formatters


class _FormatChecker(Protocol):
    def check(self, instance: object, format_: str) -> None:
        """Check if the instance validates against the format."""


@pytest.fixture
def format_checker() -> _FormatChecker:
    return util.build_format_checker(**formatters.custom_formatters())


@pytest.mark.parametrize(
    "country_code",
    ("GB",),
)
def test_country_format_with_valid_country(
    format_checker: _FormatChecker,
    country_code: str,
) -> None:
    format_checker.check(country_code, "country")


@pytest.mark.parametrize(
    "country_code",
    ("UK",),
)
def test_country_format_with_invalid_country(
    format_checker: _FormatChecker,
    country_code: str,
) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check(country_code, "country")


@pytest.mark.parametrize(
    "date_time",
    ("2022-07-12T22:06:59Z",),
)
def test_datetime_format_with_valid_datetime(
    format_checker: _FormatChecker,
    date_time: str,
) -> None:
    format_checker.check(date_time, "date-time")


@pytest.mark.parametrize(
    "date_time",
    ("2022-07-12T22:06:59",),
)
def test_datetime_format_with_invalid_datetime(
    format_checker: _FormatChecker,
    date_time: str,
) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check(date_time, "date-time")


@pytest.mark.parametrize(
    "email",
    ("foobar@example.com",),
)
def test_email_format_with_valid_email(
    format_checker: _FormatChecker,
    email: str,
) -> None:
    format_checker.check(email, "email")


@pytest.mark.parametrize(
    "email",
    ("example.com",),
)
def test_email_format_with_invalid_email(
    format_checker: _FormatChecker,
    email: str,
) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check(email, "email")


@pytest.mark.parametrize(
    "phone",
    ("+46737425447",),
)
def test_phone_format_with_valid_phone(
    format_checker: _FormatChecker,
    phone: str,
) -> None:
    format_checker.check(phone, "phone")


@pytest.mark.parametrize(
    "phone",
    (
        "0737425447",
        "0046737425447",
    ),
)
def test_phone_format_with_invalid_phone(
    format_checker: _FormatChecker,
    phone: str,
) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check(phone, "phone")


@pytest.mark.parametrize(
    "uri",
    ("https://example.com",),
)
def test_uri_format_with_valid_uri(
    format_checker: _FormatChecker,
    uri: str,
) -> None:
    format_checker.check(uri, "uri")


@pytest.mark.parametrize(
    "uri",
    ("example.com",),
)
def test_uri_format_with_invalid_uri(
    format_checker: _FormatChecker,
    uri: str,
) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check(uri, "uri")


@pytest.mark.parametrize(
    "uuid_str",
    (str(uuid.uuid4()),),
)
def test_uuid_format_with_valid_uuid(
    format_checker: _FormatChecker,
    uuid_str: str,
) -> None:
    format_checker.check(uuid_str, "uuid")


@pytest.mark.parametrize(
    "uuid_str",
    ("foobar",),
)
def test_uuid_format_with_invalid_uuid(
    format_checker: _FormatChecker,
    uuid_str: str,
) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check(uuid_str, "uuid")
