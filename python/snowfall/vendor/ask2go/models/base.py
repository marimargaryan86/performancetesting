from pydantic import BaseModel


def to_camel(string: str) -> str:
    return "".join(
        (word.title() if step else word)
        for (step, word) in enumerate(string.split("_"))
    )


class CamelCaseBaseModel(BaseModel):
    class Config(object):  # noqa: WPS431
        alias_generator = to_camel
        allow_population_by_field_name = True
