from pydantic import Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel


class Metadata(BenerailBaseModel):
    api_version: str | None = Field(
        None,
        description="The version of the API that was used to support this call.",
        example="1.0.0",
    )
    build_version: str | None = Field(
        None,
        description="The version of the software that implements this API endpoint.",
        example="MR58.0",
    )
    environment: str | None = Field(
        None,
        description="The name of the environment where the software is running.",
        example="dev_c01",
    )
    responded_at: str | None = Field(
        None,
    )
    resource_type: str | None = Field(
        None,
        description="The type of resource present in the response.",
    )
    resource_etag: str | None = Field(
        None,
        description="the etag value for the resource",
    )
