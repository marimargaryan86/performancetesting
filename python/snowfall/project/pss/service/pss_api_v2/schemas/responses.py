from typing import Any, Generic, TypeVar

from pydantic.generics import GenericModel

from snowfall.stdlib.integration.starlette.models import BaseModel

FAIL = "fail"
SUCCESS = "success"

TYPE_VAR = TypeVar("TYPE_VAR")


class ResponseSchema(GenericModel, Generic[TYPE_VAR]):
    status: str = SUCCESS
    data: TYPE_VAR  # noqa:WPS110


class ErrorResponseSchema(BaseModel):
    status: str = FAIL
    message: str
    data: Any = None  # noqa:WPS110
