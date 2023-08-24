import datetime

from pydantic import v1 as pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel
from snowfall.vendor.duffel.models.common import Airport, City, LoyaltyProgrammeAccount
from snowfall.vendor.duffel.models.offer import Offer


class OfferRequestSlice(DuffelBaseModel):
    destination_type: str
    destination: Airport | City
    origin_type: str
    origin: Airport | City
    departure_date: datetime.date


class OfferRequestPassenger(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    age: int | None
    passenger_type: str | None = pydantic.Field(alias="type")
    given_name: str | None
    family_name: str | None
    loyalty_programme_accounts: list[LoyaltyProgrammeAccount]


class OfferRequest(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    live_mode: bool
    cabin_class: str | None
    created_at: datetime.datetime
    offers: list[Offer]
    slices: list[OfferRequestSlice]
    passengers: list[OfferRequestPassenger]


class OfferRequestResponse(DuffelBaseModel):
    response_data: OfferRequest = pydantic.Field(..., alias="data")
