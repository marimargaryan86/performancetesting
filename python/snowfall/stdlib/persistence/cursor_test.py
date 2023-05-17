import base64

import pytest

from snowfall.stdlib.persistence import cursor
from snowfall.stdlib.v1 import cursor_pb2


def test_valid_cursor() -> None:
    cursor_obj = cursor.new("foobar", "foobar")

    assert cursor_obj == cursor.unmarshal(cursor.marshal(cursor_obj), "foobar")


def test_invalid_base64_string() -> None:
    with pytest.raises(cursor.CursorError):
        cursor.unmarshal("foobar")


def test_invalid_base64_string_decode() -> None:
    with pytest.raises(cursor.CursorError):
        cursor.unmarshal("MTogIjDM6IC==")


def test_invalid_protobuf_string() -> None:
    with pytest.raises(cursor.CursorError):
        cursor.unmarshal(base64.urlsafe_b64encode(b"foobar").decode())


def test_invalid_digest() -> None:
    cursor_obj = cursor_pb2.Cursor(id="foobar", filter="foobar", digest="foobar")

    with pytest.raises(cursor.CursorError):
        cursor.unmarshal(cursor.marshal(cursor_obj))


def test_invalid_filter() -> None:
    cursor_obj = cursor.new("foobar", "foobar")

    with pytest.raises(cursor.CursorError):
        cursor.unmarshal(cursor.marshal(cursor_obj), "bazqux")
