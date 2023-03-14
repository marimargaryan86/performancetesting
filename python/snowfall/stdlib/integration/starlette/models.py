from __future__ import annotations

import datetime
from typing import Any, ClassVar, Mapping, Optional, Sequence, cast

import pydantic
from starlette import background as starlette_background
from starlette import responses, status

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
    header: Optional[str]
    parameter: Optional[str]
    pointer: Optional[str]


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


class JsonApiResponse(responses.Response):
    media_type = "application/vnd.api+json"

    def __init__(
        self,
        body: Body,
        status_code: int = 200,
        headers: Mapping[str, Any] | None = None,
        background: starlette_background.BackgroundTask | None = None,
    ) -> None:
        super().__init__(
            content=body,
            status_code=int(status_code),
            headers=dict(headers or {}),
            background=background,
        )

    @classmethod
    def from_errors(cls, errors: Sequence[Error]) -> JsonApiResponse:
        status_codes = cast(set[str], {error.status for error in errors})

        if len(status_codes) == 1:
            return JsonApiResponse(
                body=Body(errors=errors),
                status_code=int(str(status_codes.pop())),
            )

        status_codes = {status_code[0] for status_code in status_codes}

        if len(status_codes) == 1 and status_codes.pop()[0] == "4":
            return JsonApiResponse(
                body=Body(errors=errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return JsonApiResponse(
            body=Body(errors=errors),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def render(self, body: Body) -> bytes:
        return body.json(
            exclude_unset=True,
            by_alias=True,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
