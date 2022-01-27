import datetime

import pytest

from snowfall.format.gtfs import normalizers


def test_normalize_currency_with_valid_currency() -> None:
    assert normalizers.normalize_currency("SEK") == "SEK"


def test_normalize_currency_with_invalid_currency() -> None:
    with pytest.raises(ValueError):
        normalizers.normalize_currency("FOO")


def test_normalize_date_with_valid_date() -> None:
    today = datetime.date.today()

    assert normalizers.normalize_date(today.strftime("%Y%m%d")) == today


@pytest.mark.parametrize("date", ["19901325", "1990-10-25"])
def test_normalize_date_with_invalid_date(date: str) -> None:
    with pytest.raises(ValueError):
        normalizers.normalize_date(date)


@pytest.mark.parametrize("language_code", ["sv-SE", "sv"])
def test_normalize_language_code_with_valid_language_code(language_code: str) -> None:
    assert normalizers.normalize_language_code(language_code) == language_code


@pytest.mark.parametrize("language_code", ["zz-ZZ", "sv-ZZ", "zz-SE"])
def test_normalize_language_code_with_invalid_language_code(language_code: str) -> None:
    with pytest.raises(ValueError):
        normalizers.normalize_language_code(language_code)


def test_normalize_phone_number_with_valid_phone_number() -> None:
    assert normalizers.normalize_phone_number("+46701234567") == "+46701234567"


def test_normalize_phone_number_with_invalid_phone_number() -> None:
    with pytest.raises(ValueError):
        normalizers.normalize_phone_number("46123")


def test_normalize_time_zone_with_valid_time_zone() -> None:
    assert normalizers.normalize_time_zone("Europe/Stockholm") == "Europe/Stockholm"


def test_normalize_time_zone_with_invalid_time_zone() -> None:
    with pytest.raises(ValueError):
        normalizers.normalize_time_zone("Europe/Uppsala")
