import pydantic

from snowfall.vendor.benerail.models.base import BenerailBaseModel


class ErrorDefinition(BenerailBaseModel):
    error_type: str | None = pydantic.Field(..., alias="type")
    title: str | None
    detail: str | None
    instance: str | None
    application: str | None
