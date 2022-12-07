from __future__ import annotations

import datetime

import pydantic

from snowfall.vendor.duffel.builders.base import DuffelRequestBaseModel


class OfferRequestSlice(DuffelRequestBaseModel):
    destination: str
    origin: str
    departure_date: datetime.date


class LoyaltyProgrammeAccount(DuffelRequestBaseModel):
    airline_iata_code: str
    account_number: str


class OfferRequestPassenger(DuffelRequestBaseModel):
    age: int | None
    pax_type: str | None = pydantic.Field(alias="type")
    given_name: str | None
    family_name: str | None
    loyalty_programme_accounts: list[LoyaltyProgrammeAccount] | None


class OfferRequestDataList(DuffelRequestBaseModel):
    passengers: list[OfferRequestPassenger]
    slices: list[OfferRequestSlice]


class OfferRequestData(DuffelRequestBaseModel):
    offer_data: OfferRequestDataList = pydantic.Field(alias="data")


class OffersRequestBuilder(object):
    def __init__(self) -> None:
        self._passengers: list[OfferRequestPassenger] = []
        self._slices: list[OfferRequestSlice] = []

    def add_passenger(self, passenger: OfferRequestPassenger) -> OffersRequestBuilder:
        self._passengers.append(passenger)
        return self

    def add_slice(self, route: OfferRequestSlice) -> OffersRequestBuilder:
        self._slices.append(route)
        return self

    def build(self) -> OfferRequestData:
        return OfferRequestData(
            offer_data=OfferRequestDataList(
                passengers=self._passengers,
                slices=self._slices,
            ),
        )
