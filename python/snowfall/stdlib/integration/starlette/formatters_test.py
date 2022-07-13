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


def test_country_format_with_valid_country(format_checker: _FormatChecker) -> None:
    format_checker.check("GB", "country")


def test_country_format_with_invalid_country(format_checker: _FormatChecker) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check("UK", "country")


def test_datetime_format_with_valid_datetime(format_checker: _FormatChecker) -> None:
    format_checker.check("2022-07-12T22:06:59Z", "date-time")


def test_datetime_format_with_invalid_datetime(format_checker: _FormatChecker) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check("2022-07-12T22:06:59", "date-time")


def test_email_format_with_valid_email(format_checker: _FormatChecker) -> None:
    format_checker.check("foobar@example.com", "email")


def test_email_format_with_invalid_email(format_checker: _FormatChecker) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check("example.com", "email")


def test_phone_format_with_valid_phone(format_checker: _FormatChecker) -> None:
    format_checker.check("+46737425447", "phone")


def test_phone_format_with_invalid_phone(format_checker: _FormatChecker) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check("0737425447", "phone")


def test_uri_format_with_valid_uri(format_checker: _FormatChecker) -> None:
    format_checker.check("https://example.com", "uri")


def test_uri_format_with_invalid_uri(format_checker: _FormatChecker) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check("example.com", "uri")


def test_uuid_format_with_valid_uuid(format_checker: _FormatChecker) -> None:
    format_checker.check(str(uuid.uuid4()), "uuid")


def test_uuid_format_with_invalid_uuid(format_checker: _FormatChecker) -> None:
    with pytest.raises(exceptions.FormatError):
        format_checker.check("foobar", "uuid")
