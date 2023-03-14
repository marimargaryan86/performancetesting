import pytest
from openapi_core.unmarshalling.schemas import (
    exceptions,
    oas30_format_unmarshallers,
    unmarshallers,
)

from snowfall.stdlib.integration.starlette import formatters


@pytest.fixture
def formats_unmarshaller() -> unmarshallers.FormatsUnmarshaller:
    return unmarshallers.FormatsUnmarshaller(
        format_unmarshallers=oas30_format_unmarshallers,
        extra_format_unmarshallers=formatters.format_unmarshallers(),
    )


@pytest.mark.parametrize(
    "schema_format,input_value",
    (
        ("country", "GB"),
        ("currency", "SEK"),
        ("date-time", "2022-07-12T22:06:59Z"),
        ("email", "foobar@example.com"),
        ("phone", "+46737425447"),
        ("uri", "https://example.com"),
        ("uuid", "1a5f9d4e-d8d5-4230-a1af-888a52ea98e8"),
    ),
)
def test_valid_formats(
    formats_unmarshaller: unmarshallers.FormatsUnmarshaller,
    schema_format: str,
    input_value: str,
) -> None:
    formats_unmarshaller.unmarshal(schema_format, input_value)


@pytest.mark.parametrize(
    "schema_format,input_value",
    (
        ("country", "UK"),
        ("currency", "XYZ"),
        ("date-time", "2022-07-12T22:06:59"),
        ("email", "example.com"),
        ("phone", "0737425447"),
        ("phone", "0046737425447"),
        ("uri", "example.com"),
        ("uuid", "foobar"),
    ),
)
def test_invalid_formats(
    formats_unmarshaller: unmarshallers.FormatsUnmarshaller,
    schema_format: str,
    input_value: str,
) -> None:
    with pytest.raises(exceptions.FormatUnmarshalError):
        formats_unmarshaller.unmarshal(schema_format, input_value)
