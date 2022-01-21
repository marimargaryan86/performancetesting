import base64

import pytest

from snowfall.common.v1alpha import models_pb2
from snowfall.persistence import cursor


def test_valid_cursor() -> None:
    cursor_obj = cursor.new("foobar", "foobar")

    assert cursor_obj == cursor.unmarshal(cursor.marshal(cursor_obj))


def test_invalid_base64_string() -> None:
    with pytest.raises(cursor.InvalidPayloadError):
        cursor.unmarshal("foobar")


def test_invalid_protobuf_string() -> None:
    with pytest.raises(cursor.InvalidPayloadError):
        cursor.unmarshal(base64.urlsafe_b64encode(b"foobar").decode())


def test_invalid_digest() -> None:
    cursor_obj = models_pb2.Cursor(id="foobar", clause="foobar", digest="foobar")

    with pytest.raises(cursor.InvalidDigestError):
        cursor.unmarshal(cursor.marshal(cursor_obj))
