from pydantic import AnyUrl, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel


class ErrorDefinition(BenerailBaseModel):
    error_type: AnyUrl | None = Field(
        None,
        example="https://example.com/probs/passenger-too-young",
        alias="type",
    )
    title: str | None = Field(
        None,
        example="Passenger too young",
    )
    detail: str | None = Field(
        None,
        description=(
            "A human readable explanation specific to this occurrence of the problem."
        ),
        example="Minimum age is 12 years for unacompanied minor.",
    )
    instance: str | None = Field(
        None,
        description="A URI of the object involved",
        example="/passengers/1245887547",
    )
    application: str | None = Field(
        None,
        description="The name of the application where the error occured.",
        example="dialogue-engine",
    )
