from pydantic.v1 import AnyUrl, ConstrainedStr, Field

from snowfall.vendor.benerail.models.base import BenerailBaseModel
from snowfall.vendor.benerail.models.bookings.enums import Optionality
from snowfall.vendor.benerail.models.link import ResourceLink


class AccommodationType(BenerailBaseModel):
    href: AnyUrl | None = None
    accommodation_type_value: str | None = Field(None, alias="value")


class Reservation(BenerailBaseModel):
    reservation_type: str | None = Field(
        None,
        description="reservation",
        example="reservation",
        alias="type",
    )
    admission: ResourceLink | None = None
    optionality: Optionality | None = None


class Admission(BenerailBaseModel):
    admission_type: str | None = Field(
        None,
        description="admission",
        example="admission",
        alias="type",
    )
    reservations: list[ResourceLink] | None = None
    is_reservation_required: bool | None = None


class BookableStatus(BenerailBaseModel):
    href: AnyUrl | None = Field(
        None,
        example="https://api.example.com/places/urn:bnds:bookable_status:BOOKABLE",
    )
    status_value: ConstrainedStr | None = Field(
        None,
        example="urn:bnds:bookable_status:BOOKABLE",
        alias="value",
        regex="^urn:[a-z]*:bookable_status:[A-Z_]*$",
    )
