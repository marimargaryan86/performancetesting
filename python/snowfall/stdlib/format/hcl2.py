from __future__ import annotations

from collections.abc import Mapping, Sequence

from hcl2 import api
from pydantic import v1 as pydantic


class Template(pydantic.BaseModel):
    data: str  # noqa: WPS110
    left_delimiter: str = "{{"
    right_delimiter: str = "}}"


class Upstream(pydantic.BaseModel):
    destination_name: str
    local_bind_port: int


class Proxy(pydantic.BaseModel):
    upstreams: Sequence[Upstream] = pydantic.Field(default_factory=list)


class SidecarService(pydantic.BaseModel):
    proxy: Sequence[Proxy] = pydantic.Field(default_factory=list)


class Check(pydantic.BaseModel):
    interval: str
    timeout: str
    type_: str = pydantic.Field(alias="type")


class Connect(pydantic.BaseModel):
    sidecar_service: Sequence[SidecarService] = pydantic.Field(default_factory=list)


class Service(pydantic.BaseModel):
    check: Sequence[Check] = pydantic.Field(default_factory=list)
    connect: Sequence[Connect] = pydantic.Field(default_factory=list)
    name: str = ""
    port: str | None
    tags: Sequence[str] = pydantic.Field(default_factory=list)


class Task(pydantic.BaseModel):
    lifecycle: Sequence[Mapping[str, str]] = pydantic.Field(default_factory=list)
    template: Sequence[Template] = pydantic.Field(default_factory=list)


class Group(pydantic.BaseModel):
    service: Sequence[Service] = pydantic.Field(default_factory=list)
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
