import pytest
from openapi_core.unmarshalling.schemas import datatypes as unmarshalling_datatypes
from openapi_core.validation.schemas import datatypes as validation_datatypes

from snowfall.stdlib.integration.openapi_core import formats


@pytest.fixture()
def format_unmarshallers() -> unmarshalling_datatypes.FormatUnmarshallersDict:
    return formats.format_unmarshallers()


@pytest.fixture()
def format_validators() -> validation_datatypes.FormatValidatorsDict:
    return formats.format_validators()


@pytest.mark.parametrize(
    ("schema_format", "input_value"),
    [
        ("country", "GB"),
        ("currency", "SEK"),
        ("date-time", "2022-07-12T22:06:59Z"),
        ("email", "foobar@example.com"),
        ("phone", "+46737425447"),
        ("uri", "https://example.com"),
    ],
)
def test_valid_formats(
    format_validators: validation_datatypes.FormatValidatorsDict,
    schema_format: str,
    input_value: str,
) -> None:
    assert format_validators[schema_format](input_value)


@pytest.mark.parametrize(
    ("schema_format", "input_value"),
    [
        ("country", "UK"),
        ("currency", "XYZ"),
        ("date-time", "2022-07-12T22:06:59"),
        ("email", "example.com"),
        ("phone", "0737425447"),
        ("phone", "0046737425447"),
        ("uri", "example.com"),
    ],
)
def test_invalid_formats(
    format_validators: validation_datatypes.FormatValidatorsDict,
    schema_format: str,
    input_value: str,
) -> None:
    assert not format_validators[schema_format](input_value)


def test_sync(
    format_unmarshallers: unmarshalling_datatypes.FormatUnmarshallersDict,
    format_validators: validation_datatypes.FormatValidatorsDict,
) -> None:
    assert format_unmarshallers.keys() == format_validators.keys()
