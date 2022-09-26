from __future__ import annotations

import datetime
from typing import Any, ClassVar, Mapping, Optional, Sequence

import pydantic
import rapidjson
from starlette import background as starlette_background
from starlette import responses

AnyMapping = Mapping[str, Any]


class BaseModel(pydantic.BaseModel):
    class Config(object):
        json_encoders = {
            datetime.datetime: lambda datetime_object: datetime_object.isoformat(
                timespec="seconds",
            ),
        }


class ResourceIdentifier(BaseModel):
    api_type: ClassVar[str]
    identifier: str = pydantic.Field(alias="id")
    data_type: str = pydantic.Field(alias="type")


class Resource(ResourceIdentifier):
    attributes: Optional[AnyMapping] = None
    relationships: Optional[AnyMapping] = None
    links: Optional[AnyMapping] = None
    meta: Optional[AnyMapping] = None


ResourceType = (
    Resource | ResourceIdentifier | Sequence[Resource] | Sequence[ResourceIdentifier]
)


class ErrorSource(BaseModel, frozen=True):
    pointer: str


class Error(BaseModel, frozen=True):
    status: Optional[str]
    code: Optional[str]
    title: Optional[str]
    detail: Optional[str]
    source: Optional[ErrorSource]


class Body(BaseModel):
    resource_data: Optional[ResourceType] = pydantic.Field(None, alias="data")
    errors: Optional[Sequence[Error]] = None
    meta: Optional[AnyMapping] = None
    links: Optional[AnyMapping] = None
    included: Optional[Sequence[Resource]] = None


class JsonApiResponse(responses.JSONResponse):
    media_type = "application/vnd.api+json"

    def __init__(
        self,
        body: Body,
        status_code: int = 200,
        headers: Optional[Mapping[str, Any]] = None,
        background: Optional[starlette_background.BackgroundTask] = None,
    ) -> None:
        super().__init__(
            content=rapidjson.loads(body.json(exclude_unset=True, by_alias=True)),
            status_code=int(status_code),
            headers=dict(headers or {}),
            background=background,
        )
