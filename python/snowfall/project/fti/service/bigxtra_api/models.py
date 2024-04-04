import typing
from collections.abc import Mapping

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field

from snowfall.stdlib import string

_examples = {
    "date-time": "2019-08-24T14:15:22Z",
    "date": "1980-02-03",
    "uuid": "04f83af5-10bb-4a0f-1881-03e1e690f0f5",
}


def add_examples(schema: Mapping[str, typing.Any]) -> None:
    for value in schema.get("properties", {}).values():
        match value:
            case {"type": "string", "format": ("date-time" | "date" | "uuid") as f}:  # noqa: WPS111
                value["example"] = _examples[f]


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        alias_generator=string.to_lower_camel,
        populate_by_name=True,
        extra="forbid",
        json_schema_extra=add_examples,
    )


class PaginationQueryParams(BaseModel):
    cursor: str = Field(
        default="",
        json_schema_extra={
            "example": "MTogIjAwNGNjOTQ5LWQ4NjYtNWM1MS05MmYxLTRjMTUxYTA4YzBjOSIgMjogIjM0ZmQwZmUzMDRhYjY3ZmIiIDM6ICIyZjhiZDU3MDljMjI3Mjg0Ig%3D%3D",
            "description": "Pagination cursor that defines your place in the list.",
        },
    )
    limit: int = Field(
        default=20,  # noqa: WPS432
        json_schema_extra={
            "minimum": 1,
            "maximum": 100,
            "example": 20,  # noqa: WPS432
            "description": "A limit on the number of objects to be returned, between 1 and 100.",
        },
    )
