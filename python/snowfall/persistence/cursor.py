import base64
import binascii
import hashlib
import hmac

from google.protobuf import text_format

from snowfall.common.v1alpha.models_pb2 import Cursor

_DIGEST_KEY = b"df8870b0-49d2-4777-994b-fa380b564df0"
_DIGEST_SIZE = 16


class CursorError(ValueError):
    """Base error that all other errors extends."""


class InvalidPayloadError(CursorError):
    """Raised when an marshalled cursor can't be decoded."""


class InvalidDigestError(CursorError):
    """Raised when an marshalled cursor contains an invalid digest."""


def unmarshal(encoded: str) -> Cursor:
    try:
        raw = base64.urlsafe_b64decode(encoded.encode()).decode()
    except binascii.Error:
        raise InvalidPayloadError()

    cursor = Cursor()

    try:
        text_format.Parse(raw, cursor, allow_field_number=True)
    except text_format.ParseError:
        raise InvalidPayloadError()

    expected_digest = _sign(Cursor(id=cursor.id, clause=cursor.clause))

    if not hmac.compare_digest(cursor.digest, expected_digest):
        raise InvalidDigestError()

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


def new(identifier: str, clause: str) -> Cursor:
    cursor = Cursor(id=identifier, clause=clause)
    cursor.digest = _sign(cursor)

    return cursor


def _sign(cursor: Cursor) -> str:
    digest = hashlib.blake2b(key=_DIGEST_KEY, digest_size=_DIGEST_SIZE)

    digest.update(text_format.MessageToBytes(cursor))

    return digest.hexdigest()
