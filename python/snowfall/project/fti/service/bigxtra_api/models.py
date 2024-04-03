import typing
from collections.abc import Mapping

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from snowfall.stdlib import string


class BaseModel(PydanticBaseModel):
    class Config:
        alias_generator = string.to_lower_camel
        populate_by_name = True
        extra = "forbid"

        @classmethod
        def json_schema_extra(
            cls,
            schema: Mapping[str, typing.Any],
        ) -> None:
            for value in schema.get("properties", {}).values():
                if value.get("type", "") == "string":
                    match value.get("format", ""):
                        case "date-time":
                            value["example"] = "2019-08-24T14:15:22Z"  # noqa: WPS220
                        case "date":
                            value["example"] = "1980-02-03"  # noqa: WPS220
                        case "uuid":
                            value["example"] = "04f83af5-10bb-4a0f-1881-03e1e690f0f5"  # noqa: WPS220


class PaginationQueryParams(BaseModel):
    cursor: str = Field(
        json_schema_extra={
            "default": "",
            "example": "MTogIjAwNGNjOTQ5LWQ4NjYtNWM1MS05MmYxLTRjMTUxYTA4YzBjOSIgMjogIjM0ZmQwZmUzMDRhYjY3ZmIiIDM6ICIyZjhiZDU3MDljMjI3Mjg0Ig%3D%3D",
            "description": "Pagination cursor that defines your place in the list.",
        },
    )
    limit: int = Field(
        json_schema_extra={
            "minimum": 1,
            "maximum": 100,
            "default": 20,  # noqa: WPS432
            "example": 20,  # noqa: WPS432
            "description": "A limit on the number of objects to be returned, between 1 and 100.",
        },
    )
