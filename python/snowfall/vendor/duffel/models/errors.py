from pydantic import v1 as pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel


class Meta(DuffelBaseModel):
    status: int | None
    request_id: str | None


class Source(DuffelBaseModel):
    pointer: str | None
    field: str | None


class Error(DuffelBaseModel):
    error_type: str | None = pydantic.Field(..., alias="type")
    title: str | None
    source: Source | str | None
    message: str | None
    documentation_url: str | None
    code: str | None


class ErrorResponse(DuffelBaseModel):
    meta: Meta | None
    errors: list[Error] | None
