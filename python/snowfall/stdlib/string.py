import re
import secrets
import string as pystring
from typing import Sequence

_default_charset = pystring.ascii_uppercase + pystring.ascii_lowercase + pystring.digits


def random(
    length: int,
    charset: Sequence[str] = _default_charset,
) -> str:
    return "".join(secrets.choice(charset) for _ in range(length))


def to_camel(string: str) -> str:
    return "".join(
        (word.title() if step else word)
        for (step, word) in enumerate(string.split("_"))
    )


def to_snake(string: str) -> str:
    return re.sub("([A-Z]+)", r"_\1", string).lower()
