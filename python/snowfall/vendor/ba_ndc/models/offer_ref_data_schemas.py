"""Contains offer ref data schemas."""
import datetime
import uuid

from pydantic import v1 as pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema


class OfferRefDataItem(BaseSchema):
    """Offer reference data item schema."""

    identifier: str = pydantic.Field(..., alias="id")
    passenger_ids: list[str] = pydantic.Field(description="Passenger ids")


class OfferRefDataPassenger(BaseSchema):
    """Offer reference passenger schema."""

    identifier: str = pydantic.Field(..., alias="id")
    ptc: str = pydantic.Field(description="Passenger ptc")
    dob: datetime.datetime | None = pydantic.Field(
        description="Passenger date of birth",
    )


class OfferRefData(BaseSchema, extra=pydantic.Extra.allow):
    """Offer reference data schema."""

    identifier: uuid.UUID = pydantic.Field(..., alias="id")
    expires_at: datetime.datetime = pydantic.Field(description="Offer expiration time")
    offer_id: str = pydantic.Field(description="External offer id")
    response_id: str = pydantic.Field(description="AirShopping response id")
    offer_ref_data_items: list[OfferRefDataItem] = pydantic.Field(
        description="Offer items",
        alias="items",
    )
    passengers: list[OfferRefDataPassenger] = pydantic.Field(
        description="Offer passengers",
    )
