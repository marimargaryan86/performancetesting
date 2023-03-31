import datetime

import pytest

from snowfall.stdlib.format.gtfs import normalizers


def test_normalize_currency_with_valid_currency() -> None:
    assert normalizers.normalize_currency("SEK") == "SEK"


def test_normalize_currency_with_invalid_currency() -> None:
    with pytest.raises(ValueError, match="is not a valid currency"):
        normalizers.normalize_currency("FOO")


@pytest.mark.parametrize(
    ("date", "expected"),
    [
        ("20220221", datetime.date.fromisoformat("2022-02-21")),
        ("2022-02-21", datetime.date.fromisoformat("2022-02-21")),
    ],
)
def test_normalize_date_with_valid_date(
    date: str,
    expected: datetime.date,
) -> None:
    assert expected == normalizers.normalize_date(date)


@pytest.mark.parametrize("date", ["19901325", "1990-13-25"])
def test_normalize_date_with_invalid_date(date: str) -> None:
    with pytest.raises(ValueError, match="is not a valid date"):
        normalizers.normalize_date(date)


@pytest.mark.parametrize(
    ("time", "expected"),
    [
        ("12:00:00", datetime.timedelta(hours=12)),  # noqa: WPS432
        ("25:12:00", datetime.timedelta(hours=25, minutes=12)),  # noqa: WPS432
        (33900.0, datetime.timedelta(hours=9, minutes=25)),  # noqa: WPS432
    ],
)
def test_normalize_time_with_valid_time(
    time: str,
    expected: datetime.timedelta,
) -> None:
    assert expected == normalizers.normalize_time(time)


@pytest.mark.parametrize("time", ["25:12"])
def test_normalize_time_with_invalid_time(time: str) -> None:
    with pytest.raises(ValueError, match="is not a valid time"):
        normalizers.normalize_time(time)


@pytest.mark.parametrize("language_code", ["sv-SE", "sv"])
def test_normalize_language_code_with_valid_language_code(language_code: str) -> None:
    assert normalizers.normalize_language_code(language_code) == language_code


@pytest.mark.parametrize("language_code", ["zz-ZZ", "sv-ZZ", "zz-SE"])
def test_normalize_language_code_with_invalid_language_code(language_code: str) -> None:
    with pytest.raises(ValueError, match="is not a valid language code"):
        normalizers.normalize_language_code(language_code)


def test_normalize_phone_number_with_valid_phone_number() -> None:
    assert normalizers.normalize_phone_number("+46701234567") == "+46701234567"


def test_normalize_phone_number_with_invalid_phone_number() -> None:
    assert not normalizers.normalize_phone_number("46123")


def test_normalize_time_zone_with_valid_time_zone() -> None:
    assert normalizers.normalize_time_zone("Europe/Stockholm") == "Europe/Stockholm"


def test_normalize_time_zone_with_invalid_time_zone() -> None:
    with pytest.raises(ValueError, match="is not a valid time zone"):
        normalizers.normalize_time_zone("Europe/Uppsala")
