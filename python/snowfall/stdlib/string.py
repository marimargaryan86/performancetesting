import re


def to_camel(string: str) -> str:
    return "".join(
        (word.title() if step else word)
        for (step, word) in enumerate(string.split("_"))
    )


def to_snake(string: str) -> str:
    return re.sub("([A-Z]+)", r"_\1", string).lower()
