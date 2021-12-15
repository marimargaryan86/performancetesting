import datetime
import json
from typing import Any, Mapping, Optional, Sequence, Union

import pydantic
from starlette import responses

AnyMapping = Mapping[str, Any]


class BaseModel(pydantic.BaseModel):
    class Config(object):  # noqa: WPS431
        arbitrary_types_allowed = True
        json_encoders = {
            datetime.datetime: lambda datetime_object: datetime_object.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
            ),
        }


class ResourceIdentifier(BaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    data_type: str = pydantic.Field(..., alias="type")


class Resource(ResourceIdentifier):
    attributes: Optional[AnyMapping] = None
    relationships: Optional[AnyMapping] = None
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
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            content=json.loads(body.json(exclude_unset=True, by_alias=True)),
            status_code=int(status_code),
            headers=headers or {},
        )
