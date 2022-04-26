def to_camel(string: str) -> str:
    return "".join(
        (word.title() if step else word)
        for (step, word) in enumerate(string.split("_"))
    )
