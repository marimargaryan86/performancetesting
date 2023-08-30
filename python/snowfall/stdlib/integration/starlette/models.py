from __future__ import annotations

import datetime
from collections.abc import Mapping, Sequence
from typing import Any, ClassVar, NotRequired, cast

import pydantic
from starlette import background as starlette_background
from starlette import responses, status
from typing_extensions import TypedDict

AnyMapping = Mapping[str, Any]


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="forbid",
        json_encoders={
            datetime.datetime: lambda datetime_object: datetime_object.isoformat(
                timespec="seconds",
            ),
        },
    )


class ResourceIdentifier(BaseModel):
    api_type: ClassVar[str]
    identifier: str = pydantic.Field(alias="id")
    data_type: str = pydantic.Field(alias="type")


class Links(TypedDict):
    next: NotRequired[str]
    related: NotRequired[str]
    self: NotRequired[str]  # noqa: WPS117


class Relationship(TypedDict):
    links: NotRequired[Links]
    data: NotRequired[  # noqa: WPS110
        Sequence[ResourceIdentifier] | ResourceIdentifier | None
    ]


Relationships = Mapping[str, Relationship]


class Resource(ResourceIdentifier):
    attributes: AnyMapping | None = None
    relationships: Relationships | None = None
    links: Links | None = None
    meta: AnyMapping | None = None


ResourceType = (
    Resource | ResourceIdentifier | Sequence[Resource] | Sequence[ResourceIdentifier]
)


class ErrorSourceHeader(BaseModel, frozen=True):
    header: str


class ErrorSourceParameter(BaseModel, frozen=True):
    parameter: str


class ErrorSourcePointer(BaseModel, frozen=True):
    pointer: str


ErrorSource = ErrorSourceHeader | ErrorSourceParameter | ErrorSourcePointer


class Error(BaseModel, frozen=True):
    status: str | None = None
    code: str | None = None
    title: str | None = None
    detail: str | None = None
    source: ErrorSource | None = None


class Body(BaseModel):
    resource_data: ResourceType | None = pydantic.Field(None, alias="data")
    errors: Sequence[Error] | None = None
    meta: AnyMapping | None = None
    links: AnyMapping | None = None
    included: Sequence[Resource] | None = None


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
            content=body.model_dump_json(
                exclude_unset=True,
                by_alias=True,
                indent=None,
            ),
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
