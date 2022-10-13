import re
import secrets
import string as pystring
import uuid as pyuuid
from typing import Sequence

_DEFAULT_CHARSET = pystring.ascii_uppercase + pystring.ascii_lowercase + pystring.digits
_DEFAULT_UUID_NAMESPACE = pyuuid.UUID("6ce93636-ac39-4130-a4f9-ea8361d61bd4")


def random(
    length: int,
    charset: Sequence[str] = _DEFAULT_CHARSET,
) -> str:
    return "".join(secrets.choice(charset) for _ in range(length))


def to_camel(string: str) -> str:
    return "".join(
        (word.title() if step else word)
        for (step, word) in enumerate(string.split("_"))
    )


def to_snake(string: str) -> str:
    return re.sub("([A-Z]+)", r"_\1", string).lower()


def to_uuid(string: str, namespace: pyuuid.UUID | None = None) -> str:
    return str(pyuuid.uuid5(namespace or _DEFAULT_UUID_NAMESPACE, string))


def uuid() -> str:
    return str(pyuuid.uuid4())
