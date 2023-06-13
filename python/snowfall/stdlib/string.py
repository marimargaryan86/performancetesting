import re
import secrets
import string as pystring
import uuid as pyuuid
from collections.abc import Sequence

_DEFAULT_CHARSET = pystring.ascii_uppercase + pystring.ascii_lowercase + pystring.digits
_DEFAULT_UUID_NAMESPACE = pyuuid.UUID("6ce93636-ac39-4130-a4f9-ea8361d61bd4")


def random(
    length: int,
    charset: Sequence[str] = _DEFAULT_CHARSET,
) -> str:
    return "".join(secrets.choice(charset) for _ in range(length))


def to_lower_camel(string: str) -> str:
    camel_case = "".join(
        (word.title() if step else word)
        for (step, word) in enumerate(
            string.replace("-", "_").replace(" ", "_").split("_"),
        )
    )

    if camel_case:
        camel_case = camel_case[0].lower() + camel_case[1:]

    return camel_case


def to_upper_camel(string: str) -> str:
    camel_case = to_lower_camel(string)

    if camel_case:
        camel_case = camel_case[0].upper() + camel_case[1:]

    return camel_case


def to_snake(string: str) -> str:
    return re.sub("(?<!^)(?=[A-Z])", "_", string).lower()


def to_uuid(string: str, namespace: pyuuid.UUID | None = None) -> str:
    return str(pyuuid.uuid5(namespace or _DEFAULT_UUID_NAMESPACE, string))


def uuid() -> str:
    return str(pyuuid.uuid4())
