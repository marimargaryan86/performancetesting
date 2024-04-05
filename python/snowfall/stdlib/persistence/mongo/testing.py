from __future__ import annotations

import datetime
from collections.abc import Mapping, Sequence

import pydantic

from snowfall.stdlib.persistence.mongo import repository
from snowfall.stdlib.v1 import testing_pb2

FoobarProto = testing_pb2.Foobar
RepeatedFoobarProto = testing_pb2.RepeatedFoobar


class ProtoRepository(repository.ProtoRepository[FoobarProto]):
    _proto = testing_pb2.Foobar


class FoobarModel(pydantic.BaseModel):
    """Pydantic version of testing_pb2.Foobar."""

    id: str = ""
    updated_at: datetime.datetime = datetime.datetime.min
    read_only: str = ""
    write_only: str = ""
    nested_foobar: FoobarModel | None = None
    struct: Mapping[str, object] = pydantic.Field(default_factory=dict)
    read_only_struct: Mapping[str, object] = pydantic.Field(default_factory=dict)


class RepeatedFoobarModel(pydantic.BaseModel):
    """Pydantic version of testing_pb2.RepeatedFoobar."""

    foobars: Sequence[FoobarModel] = pydantic.Field(default_factory=list)


class PydanticRepository(repository.PydanticRepository[FoobarModel]):
    _model = FoobarModel


class DefaultRepository(repository.DefaultRepository):
    """Extending this as well to have all repository types available in this module."""
