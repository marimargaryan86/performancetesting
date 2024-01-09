import pytest

from snowfall.stdlib import phone_number
from snowfall.stdlib.v1 import phone_number_pb2


@pytest.mark.parametrize(
    ("from_string", "to_string"),
    [
        ("+46737425447", "tel:+46-73-742-54-47"),
        ("tel:+46-73-742-54-47", "tel:+46-73-742-54-47"),
    ],
)
def test_to_and_from_string(from_string: str, to_string: str) -> None:
    assert str(phone_number.from_string(from_string)) == to_string


@pytest.mark.parametrize(
    "from_string",
    [
        "0737425447",
        "+46123",
    ],
)
def test_from_string_with_invalid_number(from_string: str) -> None:
    with pytest.raises(ValueError, match=" phone number.$"):
        phone_number.from_string(from_string)


@pytest.mark.parametrize(
    ("string_value", "extension"),
    [
        ("+46737425447", None),
        ("+46737425447", "123"),
    ],
)
def test_to_and_from_protobuf(string_value: str, extension: str | None) -> None:
    formatted = (
        "{0};ext={1}".format(string_value, extension) if extension else string_value
    )
    instance = phone_number.from_string(formatted)
    proto = instance.protobuf()

    assert proto.e164_number == string_value
    assert proto.extension == (extension or "")
    assert phone_number.from_protobuf(proto) == instance


@pytest.mark.parametrize(
    "e164_number",
    [
        "0737425447",
        "+46123",
    ],
)
def test_from_protobuf_with_invalid_number(e164_number: str) -> None:
    proto = phone_number_pb2.PhoneNumber(e164_number=e164_number)

    with pytest.raises(ValueError, match=" phone number.$"):
        phone_number.from_protobuf(proto)


def test_from_protobuf_with_short_code() -> None:
    proto = phone_number_pb2.PhoneNumber(
        short_code=phone_number_pb2.PhoneNumber.ShortCode(
            region_code="US",
            number="72404",
        ),
    )

    with pytest.raises(NotImplementedError):
        phone_number.from_protobuf(proto)


def test_from_protobuf_with_empty_message() -> None:
    proto = phone_number_pb2.PhoneNumber()

    with pytest.raises(ValueError, match=" phone number.$"):
        phone_number.from_protobuf(proto)
