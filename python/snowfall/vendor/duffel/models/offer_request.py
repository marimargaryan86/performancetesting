import datetime

import pydantic

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
    identifier: str = pydantic.Field(alias="id")
    age: int | None = None
    passenger_type: str | None = pydantic.Field(alias="type", default=None)
    given_name: str | None = None
    family_name: str | None = None
    loyalty_programme_accounts: list[LoyaltyProgrammeAccount]


class OfferRequest(DuffelBaseModel):
    identifier: str = pydantic.Field(alias="id")
    live_mode: bool
    cabin_class: str | None = None
    created_at: datetime.datetime
    offers: list[Offer]
    slices: list[OfferRequestSlice]
    passengers: list[OfferRequestPassenger]


class OfferRequestResponse(DuffelBaseModel):
    response_data: OfferRequest = pydantic.Field(alias="data")
