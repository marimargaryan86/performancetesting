import datetime
from typing import Any, Mapping, Optional, Sequence, Union

import pydantic
import rapidjson
from starlette import responses

AnyMapping = Mapping[str, Any]
Relationship = Union[AnyMapping, Sequence[AnyMapping]]


class BaseModel(pydantic.BaseModel):
    class Config(object):
        json_encoders = {
            datetime.datetime: lambda datetime_object: datetime_object.isoformat(),
        }


class ResourceIdentifier(BaseModel):
    identifier: str = pydantic.Field(alias="id")
    data_type: str = pydantic.Field(alias="type")


class Resource(ResourceIdentifier):
    attributes: Optional[AnyMapping] = None
    relationships: Optional[Relationship] = None
    links: Optional[AnyMapping] = None
    meta: Optional[AnyMapping] = None


ResourceType = Union[ResourceIdentifier, Sequence[ResourceIdentifier]]


class Error(BaseModel):
    status: str
    title: str
    detail: str


class Body(BaseModel):
    resource_data: Optional[ResourceType] = pydantic.Field(None, alias="data")
    errors: Optional[Sequence[Error]] = None
    meta: Optional[AnyMapping] = None
    links: Optional[AnyMapping] = None


class JsonApiResponse(responses.JSONResponse):
    media_type = "application/vnd.api+json"

    def __init__(
        self,
        body: Body,
        status_code: int = 200,
        headers: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(
            content=rapidjson.loads(body.json(exclude_unset=True, by_alias=True)),
            status_code=int(status_code),
            headers=dict(headers or {}),
        )
