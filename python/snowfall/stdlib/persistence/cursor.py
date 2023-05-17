import base64
import binascii
import hashlib
import hmac
from typing import Any

import orjson
from google.protobuf import text_format

from snowfall.stdlib.v1.cursor_pb2 import Cursor

_DIGEST_KEY = b"df8870b0-49d2-4777-994b-fa380b564df0"
_DIGEST_SIZE = 8  # It doesn't need to be super secure, just tamper-proofed enough.


class CursorError(ValueError):
    """Base error that all other errors extends."""


def unmarshal(encoded: str, filter_: Any = None) -> Cursor:
    cursor = _parse(encoded)
    expected_digest = _sign_cursor(Cursor(id=cursor.id, filter=cursor.filter))

    if not hmac.compare_digest(cursor.digest, expected_digest):
        raise CursorError("Invalid digest.")

    expected_hash = _hash_filter(cursor.id, filter_)

    if not hmac.compare_digest(cursor.filter, expected_hash):
        raise CursorError("Invalid filter.")

    return cursor


def marshal(cursor: Cursor) -> str:
    return base64.urlsafe_b64encode(
        text_format.MessageToBytes(
            cursor,
            as_one_line=True,
            use_short_repeated_primitives=True,
            use_field_number=True,
        ),
    ).decode()


def new(identifier: str, filter_: Any) -> Cursor:
    cursor = Cursor(id=identifier, filter=_hash_filter(identifier, filter_))
    cursor.digest = _sign_cursor(cursor)

    return cursor


def _hash_filter(identifier: str, filter_: Any) -> str:
    digest = hashlib.blake2b(key=identifier.encode(), digest_size=_DIGEST_SIZE)

    digest.update(orjson.dumps(filter_))

    return digest.hexdigest()


def _sign_cursor(cursor: Cursor) -> str:
    digest = hashlib.blake2b(key=_DIGEST_KEY, digest_size=_DIGEST_SIZE)

    digest.update(marshal(cursor).encode())

    return digest.hexdigest()


def _parse(encoded: str) -> Cursor:
    try:
        raw = base64.urlsafe_b64decode(encoded.encode()).decode()
    except (binascii.Error, UnicodeDecodeError) as err:
        raise CursorError("Invalid payload.") from err

    cursor = Cursor()

    try:
        text_format.Parse(raw, cursor, allow_field_number=True)
    except text_format.ParseError as parse_err:
        raise CursorError("Invalid payload.") from parse_err

    return cursor
