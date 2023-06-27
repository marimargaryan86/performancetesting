from __future__ import annotations

from collections.abc import Mapping, Sequence

import pydantic
from hcl2 import api


class Template(pydantic.BaseModel):
    data: str  # noqa: WPS110
    left_delimiter: str = "{{"
    right_delimiter: str = "}}"


class Task(pydantic.BaseModel):
    lifecycle: Sequence[Mapping[str, str]] = pydantic.Field(default_factory=list)
    template: Sequence[Template] = pydantic.Field(default_factory=list)


class Group(pydantic.BaseModel):
    task: Sequence[Mapping[str, Task]]


class Job(pydantic.BaseModel):
    group: Sequence[Mapping[str, Group]]


class Variable(pydantic.BaseModel):  # noqa: WPS110
    """Represent a Nomad variable."""


class Specification(pydantic.BaseModel):
    job: Sequence[Mapping[str, Job]]
    variable: Sequence[Mapping[str, Variable]]  # noqa: WPS110


def loads(text: str) -> Specification:
    parsed = api.loads(text=text)

    return Specification(**parsed)
